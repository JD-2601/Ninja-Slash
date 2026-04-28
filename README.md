# 🍉 Fruit Ninja — AI Computer Vision Edition

A real-time Fruit Ninja game controlled by your **index finger** via webcam!  
Built with **Python**, **MediaPipe** hand tracking, and **OpenCV** rendering.

---

## 🎮 How to Play

1. Stand/sit in front of your webcam
2. Raise your **index finger** — it appears as a glowing trail on screen
3. **Swipe your finger** through flying fruits to slice them
4. **Avoid bombs** (dark orbs with a fuse) — slicing them costs a life!
5. Missing a fruit also costs a life. You have **3 lives** total.

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install opencv-python mediapipe numpy

# 2. Generate cute fruit sprites
python generate_fruits.py

# 3. Launch the game!
python game.py
```

---

## 🕹️ Controls

| Key | Action |
|-----|--------|
| Index Finger | Slash fruits |
| `R` | Restart game |
| `ESC` / `Q` | Quit |

---

## 🍓 Features

- **MediaPipe** hand tracking — detects your index fingertip in real-time
- **Combo system** — slice multiple fruits quickly for bonus points
- **Particle effects** — juicy splatter on every slice
- **Floating score text** — pops up on each slice
- **Kawaii fruit sprites** — cute hand-drawn style fruits generated in code
- **Bomb hazards** — bomb = lose a life
- **Progressive difficulty** — fruits get faster over time
- **High score tracking** — persists across rounds

---

## 📁 Project Structure

```
fruit_ninja/
├── game.py              ← Main game loop
├── generate_fruits.py   ← Generates kawaii fruit PNG sprites
├── requirements.txt
├── README.md
└── assets/
    ├── apple.png
    ├── watermelon.png
    ├── orange.png
    ├── pineapple.png
    ├── strawberry.png
    ├── banana.png
    └── bomb.png
```

---

## 🔧 Customization

Inside `game.py`, tweak these at the top:

```python
LIVES = 3                 # starting lives
FRUIT_SPAWN_INTERVAL = 1.2  # seconds between spawns
BOMB_CHANCE = 0.18        # fraction of spawns that are bombs
BASE_SPEED = 5.0          # fruit launch speed
SLASH_RADIUS = 55         # how close finger needs to be to slice
COMBO_WINDOW = 0.8        # seconds to chain a combo
```

---

## 💡 Tips

- Use **fast swipe gestures** — slow hovering doesn't feel like a slash but still works
- Keep your hand at a **comfortable distance** from the camera (~50–80 cm)
- **Good lighting** dramatically improves hand detection accuracy
- You can use **both hands** simultaneously for maximum chaos!
