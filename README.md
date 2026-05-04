# DJI Tello Drone
Lab Code for Item Inspection
# 🚁 DJI Tello Autonomous Object Detection & Approach

An autonomous drone mission system built with **DJI Tello**, **YOLOv8**, and **OpenCV**.  
The drone takes off, searches the room for a target object, and autonomously approaches it until it reaches a safe proximity — then lands.

---

## 📌 Project Description

This project programs a DJI Tello drone to autonomously:
1. **Take off** and perform an initial 360° scan of the environment
2. **Search** for a specific object (e.g. a bottle) using a predefined movement pattern
3. **Approach** the detected object by centering it in the frame and moving forward
4. **Land** safely once close enough to the target

Object detection is handled in real-time using a YOLOv8 model running on the live drone camera feed.

---

## ⚙️ How It Works

### Phase 1 — Takeoff & Initial Scan
The drone takes off, hovers briefly to stabilize, then performs a full 360° clockwise rotation to scan the environment before beginning the search pattern.

```
Takeoff → Hover → Rotate 360° → Begin Search
```

### Phase 2 — Search Pattern
If the target object is not detected, the drone executes a repeating search pattern (forward movement + alternating rotations) for up to 20 iterations. After each movement step, YOLO runs on the latest camera frame to check for the target.

```
Move Forward → Rotate Right 90° → Rotate Left 90° → Repeat
         ↓
   Detection check after every step
         ↓
   Target found? → Break and enter Approach phase
```

### Phase 3 — Approach & Centering
Once the target is detected, the drone uses the bounding box position to calculate how centered the object is in the frame:

```
error_x = object_center_x - frame_center_x
```

- If `|error_x| > 50px` → rotate left or right to center the object
- If centered → move forward toward the object
- If bounding box area ≥ `Safe_Area` → the drone is close enough → stop and land

```
Detect object
    ├── Not centered → Yaw left/right
    ├── Centered     → Move forward
    └── Area ≥ Safe_Area → Hover → Land ✅
```

---

## 🧠 Code Explanation

### Key Variables

| Variable | Description |
|---|---|
| `class_ID` | YOLO class index of the target object (39 = bottle) |
| `Safe_Area` | Bounding box area threshold to trigger landing (px²) |
| `CENTER_TOL` | Pixel tolerance for centering the object (default: 50px) |
| `duration` | Sleep time in seconds between drone commands |

### Detection Logic
```python
results = YOLO_Model.predict(vid, classes=[class_ID])
```
YOLO runs on each frame captured from the drone. If any bounding boxes are returned, `Found_Target` is set to `True`.

### Proximity Estimation
Instead of using a depth sensor, proximity is estimated using the **bounding box area**:
```python
Area = width_of_box * height_of_box
```
The larger the area, the closer the drone is to the object.

### Centering & Yaw Control
```python
object_center_x = (box.xyxy[0][0] + box.xyxy[0][2]) / 2
error_x = object_center_x - frame_center_x

yaw = -20 if error_x > 0 else 20
tello.send_rc_control(0, 0, 0, yaw)
```
The drone rotates until the object is within the center tolerance before moving forward.

---

## 🛠️ Requirements

- DJI Tello drone
- Python 3.8+
- Libraries:
```
djitellopy
ultralytics
opencv-python
```

Install with:
```bash
pip install djitellopy ultralytics opencv-python
```

---

## 🚀 Usage

1. Connect your PC to the Tello's Wi-Fi network
2. Place your YOLO model file (`yolo26n.pt`) in the project directory
3. Run the script:
```bash
python drone_detection.py
```

> ⚠️ Make sure you have enough open space before running. The drone will move autonomously.

---

## 📁 Project Structure

```
├── drone_detection.py   # Main script
├── yolo26n.pt           # YOLOv8 model weights
└── README.md
```