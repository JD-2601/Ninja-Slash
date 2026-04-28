"""Generate cute kawaii fruit sprites as PNG files."""
import numpy as np
import cv2
import os

os.makedirs("assets", exist_ok=True)

def draw_cute_face(img, cx, cy, size):
    """Draw kawaii face on fruit."""
    eye_r = max(4, size // 14)
    offset = size // 7
    # Eyes
    cv2.circle(img, (cx - offset, cy), eye_r, (30, 30, 30, 255), -1)
    cv2.circle(img, (cx + offset, cy), eye_r, (30, 30, 30, 255), -1)
    # Eye shine
    cv2.circle(img, (cx - offset + 2, cy - 2), max(1, eye_r // 2), (255, 255, 255, 255), -1)
    cv2.circle(img, (cx + offset + 2, cy - 2), max(1, eye_r // 2), (255, 255, 255, 255), -1)
    # Smile
    cv2.ellipse(img, (cx, cy + size // 8), (size // 8, size // 12), 0, 0, 180, (30, 30, 30, 255), 2)
    # Rosy cheeks
    cv2.circle(img, (cx - offset - 4, cy + 5), eye_r + 1, (180, 100, 180, 80), -1)
    cv2.circle(img, (cx + offset + 4, cy + 5), eye_r + 1, (180, 100, 180, 80), -1)


def make_apple(size=90):
    img = np.zeros((size, size, 4), dtype=np.uint8)
    cx, cy = size // 2, size // 2 + 6
    r = size // 2 - 8
    # Shadow
    cv2.ellipse(img, (cx, cy + r - 2), (r, r // 3), 0, 0, 360, (0, 0, 0, 40), -1)
    # Body
    cv2.circle(img, (cx, cy), r, (40, 40, 210, 255), -1)
    # Highlight
    cv2.circle(img, (cx - r // 3, cy - r // 3), r // 3, (120, 120, 240, 180), -1)
    # Indentation top
    cv2.circle(img, (cx, cy - r + 3), 5, (30, 30, 180, 255), -1)
    # Stem
    cv2.line(img, (cx, cy - r + 3), (cx + 6, cy - r - 12), (80, 50, 20, 255), 3)
    # Leaf
    pts = np.array([[cx + 6, cy - r - 8], [cx + 22, cy - r - 18], [cx + 14, cy - r - 3]])
    cv2.fillPoly(img, [pts], (30, 160, 30, 255))
    draw_cute_face(img, cx, cy + 4, size)
    return img


def make_watermelon(size=90):
    img = np.zeros((size, size, 4), dtype=np.uint8)
    cx, cy = size // 2, size // 2 + 4
    r = size // 2 - 6
    # Green rind
    cv2.circle(img, (cx, cy), r, (30, 140, 30, 255), -1)
    # Red flesh
    cv2.circle(img, (cx, cy), int(r * 0.82), (50, 60, 220, 255), -1)
    # Highlight
    cv2.circle(img, (cx - r // 3, cy - r // 3), r // 4, (120, 120, 255, 120), -1)
    # Seeds
    for sx, sy in [(-14, 5), (0, -8), (14, 5), (-6, 18)]:
        cv2.ellipse(img, (cx + sx, cy + sy), (4, 7), 30, 0, 360, (20, 20, 60, 255), -1)
    draw_cute_face(img, cx, cy - 2, size)
    return img


def make_orange(size=90):
    img = np.zeros((size, size, 4), dtype=np.uint8)
    cx, cy = size // 2, size // 2 + 4
    r = size // 2 - 7
    # Body
    cv2.circle(img, (cx, cy), r, (30, 140, 230, 255), -1)
    # Texture lines (segments)
    for angle in range(0, 360, 45):
        rad = np.radians(angle)
        x2 = int(cx + r * 0.8 * np.cos(rad))
        y2 = int(cy + r * 0.8 * np.sin(rad))
        cv2.line(img, (cx, cy), (x2, y2), (20, 120, 210, 120), 1)
    # Center dot
    cv2.circle(img, (cx, cy), 4, (20, 110, 200, 255), -1)
    # Highlight
    cv2.circle(img, (cx - r // 3, cy - r // 3), r // 3, (100, 190, 255, 150), -1)
    # Stem + leaf
    cv2.line(img, (cx, cy - r), (cx, cy - r - 10), (60, 40, 20, 255), 3)
    pts = np.array([[cx, cy - r - 5], [cx + 15, cy - r - 15], [cx + 8, cy - r + 2]])
    cv2.fillPoly(img, [pts], (30, 160, 30, 255))
    draw_cute_face(img, cx, cy + 5, size)
    return img


def make_pineapple(size=100):
    img = np.zeros((size, size, 4), dtype=np.uint8)
    cx, cy = size // 2, size // 2 + 10
    # Body (oval)
    cv2.ellipse(img, (cx, cy), (size // 3, size // 2 - 12), 0, 0, 360, (30, 180, 220, 255), -1)
    # Cross-hatch pattern
    for i in range(-4, 5):
        y = cy + i * 10
        x_off = (i % 2) * 5
        for j in range(-2, 3):
            px = cx + j * 14 + x_off
            if 0 < px < size and 0 < y < size:
                cv2.circle(img, (px, y), 4, (20, 160, 200, 255), -1)
                cv2.circle(img, (px, y), 4, (10, 140, 180, 100), 1)
    # Crown leaves
    leaf_colors = [(20, 160, 30, 255), (30, 180, 40, 255), (15, 140, 25, 255)]
    for i, (lx, ly, angle) in enumerate([(-18, -20, -30), (0, -28, 0), (18, -20, 30)]):
        color = leaf_colors[i % 3]
        pts = np.array([
            [cx + lx, cy - size // 2 + 12],
            [cx + lx + int(12 * np.cos(np.radians(angle - 90))),
             cy - size // 2 + 12 + ly + int(12 * np.sin(np.radians(angle - 90)))],
            [cx + lx + 8, cy - size // 2 + 20]
        ])
        cv2.fillPoly(img, [pts], color)
    draw_cute_face(img, cx, cy + 5, size)
    return img


def make_strawberry(size=90):
    img = np.zeros((size, size, 4), dtype=np.uint8)
    cx, cy = size // 2, size // 2 + 8
    r = size // 2 - 8
    # Draw strawberry shape (heart-ish, pointy bottom)
    pts = []
    for a in range(0, 360, 3):
        rad = np.radians(a)
        # Custom polar shape: wider top, pointy bottom
        rr = r * (0.9 + 0.1 * np.cos(2 * rad)) * (1 - 0.3 * np.sin(rad))
        x = int(cx + rr * np.sin(rad))
        y = int(cy - rr * np.cos(rad))
        pts.append([x, y])
    pts = np.array(pts)
    cv2.fillPoly(img, [pts], (50, 50, 210, 255))
    # Seeds
    for sx, sy in [(-10, -5), (8, -10), (-4, 10), (12, 8), (0, 0)]:
        cv2.ellipse(img, (cx + sx, cy + sy), (2, 4), 15, 0, 360, (220, 220, 255, 255), -1)
    # Leaves
    for angle in [-20, 0, 20]:
        rad = np.radians(angle - 90)
        lx = int(cx + 12 * np.cos(rad))
        ly = int(cy - r + 8 + 12 * np.sin(rad))
        pts_l = np.array([
            [cx, cy - r + 8],
            [lx, ly],
            [lx + 5, cy - r + 15]
        ])
        cv2.fillPoly(img, [pts_l], (30, 160, 30, 255))
    draw_cute_face(img, cx, cy + 2, size)
    return img


def make_banana(size=100):
    img = np.zeros((size, size, 4), dtype=np.uint8)
    # Curved banana shape using polyline
    points = []
    for t in np.linspace(0, np.pi, 30):
        x = int(15 + (size - 30) * t / np.pi)
        y = int(size // 2 + 20 - 30 * np.sin(t))
        points.append([x, y])
    # Create thick curve (top and bottom)
    top_pts = []
    bot_pts = []
    for t in np.linspace(0, np.pi, 30):
        x = int(12 + (size - 24) * t / np.pi)
        ty = int(size // 2 + 15 - 28 * np.sin(t))
        by = int(size // 2 + 28 - 22 * np.sin(t))
        top_pts.append([x, ty])
        bot_pts.append([x, by])
    poly = np.array(top_pts + bot_pts[::-1])
    cv2.fillPoly(img, [poly], (30, 210, 230, 255))
    # Shine
    shine_pts = []
    for t in np.linspace(0.2, 0.8, 15):
        x = int(12 + (size - 24) * t)
        y = int(size // 2 + 17 - 26 * np.sin(t * np.pi))
        shine_pts.append([x, y])
    if shine_pts:
        for p in shine_pts:
            cv2.circle(img, tuple(p), 3, (100, 240, 255, 120), -1)
    # Face in middle
    mid_x = size // 2
    mid_y = size // 2 + 5
    draw_cute_face(img, mid_x, mid_y, size // 2)
    return img


def make_bomb(size=80):
    """Bomb - player loses life if slashed."""
    img = np.zeros((size, size, 4), dtype=np.uint8)
    cx, cy = size // 2, size // 2 + 4
    r = size // 2 - 8
    # Body
    cv2.circle(img, (cx, cy), r, (30, 30, 30, 255), -1)
    # Shine
    cv2.circle(img, (cx - r // 3, cy - r // 3), r // 4, (80, 80, 80, 200), -1)
    # Fuse
    cv2.line(img, (cx, cy - r), (cx + 8, cy - r - 12), (80, 60, 20, 255), 3)
    # Spark
    cv2.circle(img, (cx + 8, cy - r - 14), 5, (0, 200, 240, 255), -1)
    cv2.circle(img, (cx + 10, cy - r - 16), 3, (0, 240, 255, 255), -1)
    # Angry face
    eye_r = 5
    cv2.circle(img, (cx - 10, cy - 3), eye_r, (200, 50, 50, 255), -1)
    cv2.circle(img, (cx + 10, cy - 3), eye_r, (200, 50, 50, 255), -1)
    # Angry brows
    cv2.line(img, (cx - 15, cy - 12), (cx - 5, cy - 8), (200, 50, 50, 255), 3)
    cv2.line(img, (cx + 5, cy - 8), (cx + 15, cy - 12), (200, 50, 50, 255), 3)
    # Frown
    cv2.ellipse(img, (cx, cy + 10), (10, 6), 0, 180, 360, (200, 50, 50, 255), 2)
    return img


# Generate and save all fruits
fruits = {
    "apple": make_apple(),
    "watermelon": make_watermelon(),
    "orange": make_orange(),
    "pineapple": make_pineapple(),
    "strawberry": make_strawberry(),
    "banana": make_banana(),
    "bomb": make_bomb(),
}

for name, img in fruits.items():
    path = f"assets/{name}.png"
    cv2.imwrite(path, img)
    print(f"Saved {path} - shape: {img.shape}")

print("All fruits generated!")
