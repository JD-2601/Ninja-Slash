# Fruit Ninja with computer vision



import cv2
import mediapipe as mp
import numpy as np
import random
import time
import math
import os

#  Configuration

WINDOW_NAME = "🍉 Fruit Ninja"
LIVES = 3
FRUIT_SPAWN_INTERVAL = 1.2   # seconds between spawns
BOMB_CHANCE = 0.18            # probability a spawn is a bomb
SPEED_INCREASE = 0.0005       # speed scales with time
BASE_SPEED = 30.0
SLASH_TRAIL_LEN = 20          # finger trail history length
SLASH_RADIUS = 120             # collision detection radius (px)
PARTICLE_COUNT = 12           # juice particles on slice
COMBO_WINDOW = 0.8            # seconds to chain combos

HEART = "♥"
SKULL = "☠"

FRUIT_NAMES = ["apple", "watermelon", "orange", "pineapple", "strawberry", "banana"]
FRUIT_COLORS = {
    "apple":       (210, 40,  40),
    "watermelon":  (50,  220, 50),
    "orange":      (30,  160, 240),
    "pineapple":   (30,  210, 220),
    "strawberry":  (60,  60,  220),
    "banana":      (30,  210, 240),
    "bomb":        (60,  60,  60),
}



#  Asset loading

def load_assets():
    assets = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.join(script_dir, "assets")
    for name in FRUIT_NAMES + ["bomb"]:
        path = os.path.join(asset_dir, f"{name}.png")
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None and img.shape[2] == 4:
                assets[name] = img
    return assets



#  Utility: overlay RGBA image on BGR frame

def overlay_image(frame, img_rgba, x, y, scale=1.0, alpha_mult=1.0):
    if img_rgba is None:
        return
    if scale != 1.0:
        h, w = img_rgba.shape[:2]
        img_rgba = cv2.resize(img_rgba, (max(1, int(w * scale)), max(1, int(h * scale))))

    h, w = img_rgba.shape[:2]
    fh, fw = frame.shape[:2]

    x1, y1 = int(x - w // 2), int(y - h // 2)
    x2, y2 = x1 + w, y1 + h

    # Clip to frame
    ix1, iy1 = max(0, x1), max(0, y1)
    ix2, iy2 = min(fw, x2), min(fh, y2)
    if ix2 <= ix1 or iy2 <= iy1:
        return

    # Corresponding region in sprite
    sx1, sy1 = ix1 - x1, iy1 - y1
    sx2, sy2 = sx1 + (ix2 - ix1), sy1 + (iy2 - iy1)

    roi = frame[iy1:iy2, ix1:ix2]
    sprite_bgr = img_rgba[sy1:sy2, sx1:sx2, :3]
    alpha = img_rgba[sy1:sy2, sx1:sx2, 3:4].astype(np.float32) / 255.0 * alpha_mult
    frame[iy1:iy2, ix1:ix2] = (sprite_bgr * alpha + roi * (1 - alpha)).astype(np.uint8)


#  Particle system

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(2, 5)
        self.life = 1.0
        self.decay = random.uniform(0.04, 0.09)
        self.radius = random.randint(4, 10)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4   # gravity
        self.life -= self.decay
        return self.life > 0

    def draw(self, frame):
        if self.life <= 0:
            return
        a = int(self.life * 255)
        x, y = int(self.x), int(self.y)
        cv2.circle(frame, (x, y), self.radius,
                   (self.color[0], self.color[1], self.color[2]), -1)



#  Floating score text

class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x, self.y = float(x), float(y)
        self.text = text
        self.color = color
        self.life = 1.0

    def update(self):
        self.y -= 1.5
        self.life -= 0.035
        return self.life > 0

    def draw(self, frame):
        if self.life <= 0:
            return
        alpha = self.life
        scale = 1.0 + (1 - self.life) * 0.5
        font_scale = 1.2 * scale
        thickness = max(1, int(2 * scale))
        color = tuple(int(c * alpha) for c in self.color)
        cv2.putText(frame, self.text, (int(self.x), int(self.y)),
                    cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 0, 0), thickness + 2)
        cv2.putText(frame, self.text, (int(self.x), int(self.y)),
                    cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness)



#  Fruit / Bomb object

class Fruit:
    def __init__(self, fw, fh, elapsed, assets):
        self.fw, self.fh = fw, fh
        self.is_bomb = random.random() < BOMB_CHANCE
        self.name = "bomb" if self.is_bomb else random.choice(FRUIT_NAMES)
        self.img = assets.get(self.name)

        # Physics – launch from bottom
        self.x = random.uniform(fw * 0.15, fw * 0.85)
        self.y = float(fh + 60)
        speed = BASE_SPEED + elapsed * SPEED_INCREASE + random.uniform(-1, 2)
        angle = -math.pi / 2
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.rotation = 0.0
        self.rot_speed = random.uniform(-5, 5)
        self.scale = random.uniform(0.8, 1.3)
        self.alive = True
        self.sliced = False
        self.slice_alpha = 1.0

        # Half-pieces after slice
        self.half_left = None
        self.half_right = None

    def update(self, gravity=0.005):
        self.vy += gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed

        if self.sliced:
            self.slice_alpha -= 0.05
            if self.slice_alpha <= 0:
                self.alive = False
        elif self.y > self.fh + 100:
            self.alive = False

    def draw(self, frame):
        if not self.alive or self.img is None:
            return
        # Rotate sprite
        h, w = self.img.shape[:2]
        cx, cy = w // 2, h // 2
        M = cv2.getRotationMatrix2D((cx, cy), self.rotation, 1.0)
        rotated = cv2.warpAffine(self.img, M, (w, h), flags=cv2.INTER_LINEAR,
                                  borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        alpha = self.slice_alpha if self.sliced else 1.0
        overlay_image(frame, rotated, int(self.x), int(self.y), self.scale, alpha)

    def check_slash(self, sx, sy):
        if not self.alive or self.sliced:
            return False
        dx = sx - self.x
        dy = sy - self.y
        return math.sqrt(dx * dx + dy * dy) < SLASH_RADIUS


#  Hand tracker (MediaPipe)

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )

    def get_fingertips(self, frame_rgb):
        """Return list of (x, y) fingertip positions (index finger tip)."""
        results = self.hands.process(frame_rgb)
        tips = []
        if results.multi_hand_landmarks:
            h, w = frame_rgb.shape[:2]
            for hand_lm in results.multi_hand_landmarks:
                # Landmark 8 = index finger tip
                lm = hand_lm.landmark[8]
                tips.append((int(lm.x * w), int(lm.y * h)))
        return tips

    def release(self):
        self.hands.close()



#  UI drawing helpers

def draw_hud(frame, score, lives, combo, high_score):
    h, w = frame.shape[:2]

    # Semi-transparent top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    # Score
    cv2.putText(frame, f"Score: {score}", (20, 42),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 4)
    cv2.putText(frame, f"Score: {score}", (20, 42),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 230, 80), 2)

    # High score
    cv2.putText(frame, f"Best: {high_score}", (w // 2 - 60, 42),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 3)
    cv2.putText(frame, f"Best: {high_score}", (w // 2 - 60, 42),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, (200, 200, 255), 1)

    # Lives (hearts)
    for i in range(lives):
        cx = w - 40 - i * 38
        cv2.circle(frame, (cx, 30), 14, (0, 0, 0), -1)
        cv2.circle(frame, (cx, 30), 12, (0, 50, 200), -1)
        cv2.putText(frame, HEART, (cx - 9, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 255), 2)

    # Combo
    if combo >= 2:
        combo_text = f"COMBO x{combo}!"
        color = (0, 200, 255) if combo < 4 else (0, 80, 255)
        cv2.putText(frame, combo_text, (w // 2 - 70, h - 30),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 0, 0), 5)
        cv2.putText(frame, combo_text, (w // 2 - 70, h - 30),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, color, 2)


def draw_slash_trail(frame, trail, color=(180, 255, 255)):
    """Draw glowing finger trail."""
    if len(trail) < 2:
        return
    for i in range(1, len(trail)):
        alpha = i / len(trail)
        thickness = max(1, int(alpha * 8))
        t_color = tuple(int(c * alpha) for c in color)
        cv2.line(frame, trail[i - 1], trail[i], (0, 0, 0), thickness + 3)
        cv2.line(frame, trail[i - 1], trail[i], t_color, thickness)
    # Glow dot at tip
    if trail:
        cv2.circle(frame, trail[-1], 10, (255, 255, 255), -1)
        cv2.circle(frame, trail[-1], 7, color, -1)


def draw_game_over(frame, score, high_score):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    cy = h // 2
    cv2.putText(frame, "GAME OVER", (w // 2 - 180, cy - 70),
                cv2.FONT_HERSHEY_DUPLEX, 2.2, (0, 0, 0), 8)
    cv2.putText(frame, "GAME OVER", (w // 2 - 180, cy - 70),
                cv2.FONT_HERSHEY_DUPLEX, 2.2, (0, 80, 230), 4)

    cv2.putText(frame, f"Score: {score}", (w // 2 - 100, cy),
                cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 230, 80), 3)
    if score >= high_score:
        cv2.putText(frame, "NEW HIGH SCORE!", (w // 2 - 160, cy + 55),
                    cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 220, 255), 2)
    else:
        cv2.putText(frame, f"Best: {high_score}", (w // 2 - 90, cy + 55),
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (200, 200, 200), 2)

    cv2.putText(frame, "Press R to restart | ESC to quit",
                (w // 2 - 230, cy + 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)


def draw_countdown(frame, count):
    h, w = frame.shape[:2]
    text = str(count) if count > 0 else "GO!"
    color = (0, 200, 255) if count > 0 else (50, 255, 100)
    size = 4.0
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, size, 4)
    cv2.putText(frame, text, (w // 2 - tw // 2, h // 2 + th // 2),
                cv2.FONT_HERSHEY_DUPLEX, size, (0, 0, 0), 12)
    cv2.putText(frame, text, (w // 2 - tw // 2, h // 2 + th // 2),
                cv2.FONT_HERSHEY_DUPLEX, size, color, 4)


#  Main game loop

def main():
    assets = load_assets()
    if not assets:
        print("⚠️  No assets found. Run generate_fruits.py first!")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    tracker = HandTracker()

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1280, 720)

    # ── Game state ──
    def reset_game():
        return {
            "score": 0,
            "lives": LIVES,
            "fruits": [],
            "particles": [],
            "floats": [],
            "trails": {},        # hand_index -> deque of points
            "last_spawn": time.time(),
            "start_time": time.time(),
            "game_over": False,
            "combo": 0,
            "last_slice_time": 0.0,
        }

    state = reset_game()
    high_score = 0
    countdown_start = time.time()
    countdown_duration = 3
    in_countdown = True

    print("🍉 Fruit Ninja started! Point your index finger to slash fruits.")
    print("   Press ESC or Q to quit, R to restart.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Mirror
        fh, fw = frame.shape[:2]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        now = time.time()

        # ── Hand tracking ──
        fingertips = tracker.get_fingertips(frame_rgb)

        # ── Countdown screen ──
        if in_countdown:
            elapsed_cd = now - countdown_start
            count = max(0, countdown_duration - int(elapsed_cd))
            draw_countdown(frame, count)
            if elapsed_cd >= countdown_duration + 0.5:
                in_countdown = False
                state["start_time"] = time.time()
                state["last_spawn"] = time.time()
            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break
            continue

        # ── Game Over screen ──
        if state["game_over"]:
            draw_game_over(frame, state["score"], high_score)
            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break
            if key == ord('r'):
                state = reset_game()
                countdown_start = time.time()
                in_countdown = True
            continue

        elapsed = now - state["start_time"]

        # ── Spawn fruits ──
        spawn_interval = max(0.5, FRUIT_SPAWN_INTERVAL - elapsed * 0.002)
        if now - state["last_spawn"] > spawn_interval:
            # Spawn 1-3 fruits at once for fun
            count = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            for _ in range(count):
                state["fruits"].append(Fruit(fw, fh, elapsed, assets))
            state["last_spawn"] = now

        # ── Update trails ──
        for i, tip in enumerate(fingertips):
            trail = state["trails"].setdefault(i, [])
            trail.append(tip)
            if len(trail) > SLASH_TRAIL_LEN:
                trail.pop(0)

        # Remove stale trails
        for k in list(state["trails"].keys()):
            if k >= len(fingertips):
                state["trails"].pop(k)

        # ── Collision detection ──
        for tip in fingertips:
            sx, sy = tip
            for fruit in state["fruits"]:
                if fruit.alive and not fruit.sliced and fruit.check_slash(sx, sy):
                    fruit.sliced = True
                    color = FRUIT_COLORS.get(fruit.name, (200, 200, 200))

                    if fruit.is_bomb:
                        # Bomb hit - lose life
                        state["lives"] -= 1
                        state["combo"] = 0
                        for _ in range(PARTICLE_COUNT):
                            state["particles"].append(
                                Particle(fruit.x, fruit.y, (40, 40, 200)))
                        state["floats"].append(
                            FloatingText(int(fruit.x) - 30, int(fruit.y),
                                         f"-1 {SKULL}", (0, 0, 220)))
                        if state["lives"] <= 0:
                            high_score = max(high_score, state["score"])
                            state["game_over"] = True
                    else:
                        # Fruit sliced - score!
                        if now - state["last_slice_time"] < COMBO_WINDOW:
                            state["combo"] += 1
                        else:
                            state["combo"] = 1
                        state["last_slice_time"] = now

                        pts = state["combo"]
                        state["score"] += pts

                        for _ in range(PARTICLE_COUNT):
                            state["particles"].append(Particle(fruit.x, fruit.y, color))

                        label = f"+{pts}" if pts == 1 else f"+{pts} COMBO!"
                        text_color = (255, 255, 255) if pts == 1 else (0, 220, 255)
                        state["floats"].append(
                            FloatingText(int(fruit.x) - 20, int(fruit.y), label, text_color))

        # ── Check missed fruits (not bombs - only fruits cause life loss when missed) ──
        for fruit in state["fruits"]:
            if fruit.alive and not fruit.sliced and fruit.y > fh + 80:
                if not fruit.is_bomb:
                    state["lives"] -= 1
                    state["floats"].append(
                        FloatingText(int(fruit.x), fh - 40, "Missed!", (0, 100, 255)))
                    if state["lives"] <= 0:
                        high_score = max(high_score, state["score"])
                        state["game_over"] = True
                fruit.alive = False  # mark gone either way

        # ── Update all objects ──
        state["fruits"] = [f for f in state["fruits"] if f.update() or f.alive]
        state["particles"] = [p for p in state["particles"] if p.update()]
        state["floats"] = [ft for ft in state["floats"] if ft.update()]

        # ── Draw fruits ──
        for fruit in state["fruits"]:
            fruit.draw(frame)

        # ── Draw particles ──
        for p in state["particles"]:
            p.draw(frame)

        # ── Draw slash trails ──
        trail_colors = [(180, 255, 200), (200, 180, 255), (255, 230, 150)]
        for i, trail in state["trails"].items():
            color = trail_colors[i % len(trail_colors)]
            draw_slash_trail(frame, trail, color)

        # ── Draw floating texts ──
        for ft in state["floats"]:
            ft.draw(frame)

        # ── HUD ──
        draw_hud(frame, state["score"], state["lives"], state["combo"], high_score)

        # ── FPS ──
        cv2.putText(frame, f"FPS: {cap.get(cv2.CAP_PROP_FPS):.0f}",
                    (fw - 110, fh - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        if key == ord('r'):
            state = reset_game()
            countdown_start = time.time()
            in_countdown = True

    cap.release()
    tracker.release()
    cv2.destroyAllWindows()
    print(f"\n🏆 Final High Score: {high_score}")
    print("Thanks for playing! 🍉")


if __name__ == "__main__":
    main()
