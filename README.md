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

## 🎬 Demo

> Trial run — battery ran out before the full approach completed, but the detection, search pattern, and centering phases all worked as expected. Other trials confirmed the full pipeline runs end to end.

[▶️ Watch on LinkedIn](https://www.linkedin.com/posts/abdelrahman-tayel)

---

## ⚙️ How It Works

### Phase 1 — Takeoff & Initial Scan
The drone takes off, hovers briefly to stabilize, then performs a full 360° clockwise rotation to scan the environment before beginning the search pattern.

```
Takeoff → Hover → Rotate 360° → Begin Search
```

### Phase 2 — Search Pattern
If the target object is not detected, the drone executes a repeating search pattern (forward movement + alternating rotations). After each movement step, YOLO runs on the latest camera frame to check for the target.

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

### Phase 4 — Concurrent Architecture
The system uses a custom `TelloTimer` threading model, separating the camera and flight loops:

```
camera_loop  → every 30ms  →  YOLO detection + frame display
flight_loop  → every 100ms →  RC commands based on detection results
```

This ensures the camera feed and flight control never block each other.

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

## ⚠️ Known Issues / Limitations

- **Battery life** — The Tello battery (~13 min) can run out mid-mission during long search patterns. Calibrate `Safe_Area` and search pattern length for your space.
- **No depth sensor** — Proximity is estimated via bounding box area, which varies with object size. A larger object will trigger landing earlier than a smaller one at the same distance.
- **Single target** — The system locks onto the first detected object of the target class. Behavior is undefined if multiple objects are visible.
- **Static Safe_Area** — The landing threshold is hardcoded. Calibrate it by printing the `Area` value at your desired landing distance.
- **No obstacle avoidance** — The drone moves forward blindly once centered. Use in open spaces only.

---

## 🔭 Future Ideas

Extensions worth building on top of this project:

- 🔹 **Search & retrieve** — detect an object, simulate a grab, and return to a home position
- 🔹 **Multi-target prioritization** — detect multiple objects and rank them by distance or confidence
- 🔹 **Obstacle avoidance** — use camera-based depth estimation to avoid walls and furniture
- 🔹 **GPS-guided return** — navigate back to the launch point after mission completion
- 🔹 **Face or gesture recognition** — swap the object detector for a face detector and follow a person
- 🔹 **PID-based approach** — replace fixed yaw/speed values with a PID controller for smoother movement
- 🔹 **Altitude control** — add vertical centering (error_y) so the drone adjusts height to keep the target centered vertically

---

## 🛠️ Requirements

- DJI Tello drone
- Python 3.8+

```bash
pip install djitellopy ultralytics opencv-python pynput
```

---

## 🚀 Usage

1. Connect your PC to the Tello's Wi-Fi network
2. Place your YOLO model file (e.g. `yolov8n.pt`) in the project directory
3. Run:
```bash
python drone_detection.py
```

> ⚠️ Make sure you have enough open space. The drone moves autonomously.  
> Press **Space** at any time for an emergency stop.

---

## 📁 Project Structure

```
├── drone_detection.py   # Main script
├── yolov8n.pt           # YOLOv8 model weights
└── README.md
```