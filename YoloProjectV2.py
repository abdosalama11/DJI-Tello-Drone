# Libraries
###################################
import time, cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
from threading import Thread, Event
from djitellopy import Tello

# Setup
###################################
tello = Tello()
tello.connect()
tello.streamon()

YOLO_Model = YOLO("yolo26n.pt")
frame_read = tello.get_frame_read()

# Variables
###################################
duration = 2
class_ID = 39
Found_Target = False
Safe_Area = 120000
CENTER_TOL = 50
Area = 0
error_x = 0
stop_event = Event()

# ─── TelloTimer ───────────────────────────────────────────
class TelloTimer(Thread):
    def __init__(self, interval, event, func):
        Thread.__init__(self)
        self.running = event
        self.interval = interval
        self.func = func
        self.daemon = True

    def run(self):
        while not self.running.wait(self.interval):
            self.func()

# ─── Camera Loop ──────────────────────────────────────────
def camera_loop():
    global Found_Target, Area, error_x

    if stop_event.is_set():
        return

    frame = frame_read.frame
    vid = frame.copy()

    results = YOLO_Model.predict(vid, classes=[class_ID], verbose=False)
    annotator = Annotator(vid, line_width=2, font_size=10)

    if len(results[0].boxes) > 0:
        Found_Target = True

    if Found_Target:
        frame_center_x = vid.shape[1] / 2
        Area = 0
        error_x = 0

        for obj in results:
            for box in obj.boxes:
                label = YOLO_Model.names[int(box.cls)] + " (" + str(round(float(box.conf[0]), 2)) + ")"
                annotator.box_label(box.xyxy[0], label)

                x_D = abs(int(box.xyxy[0][0]) - int(box.xyxy[0][2]))
                y_D = abs(int(box.xyxy[0][1]) - int(box.xyxy[0][3]))
                Area = x_D * y_D
                print(Area)

                object_center_x = (box.xyxy[0][0] + box.xyxy[0][2]) / 2
                error_x = object_center_x - frame_center_x

                print(f"Area: {Area} | error_x: {error_x:.1f}")

    cv2.imshow("Results", annotator.result())
    cv2.waitKey(1)

# ─── Flight Loop ──────────────────────────────────────────
def flight_loop():
    global Found_Target, Area, error_x

    if stop_event.is_set():
        return

    if not Found_Target:
        speed = 10
        rotation = 15
        #tello.send_rc_control(0, speed, 0, 0)
        #time.sleep(duration)
        tello.rotate_clockwise(rotation)
        time.sleep(duration)

    else:
        if Area >= Safe_Area:
            tello.send_rc_control(0, 0, 0, 0)
            time.sleep(duration)
            tello.land()
            stop_event.set()

        elif abs(error_x) > CENTER_TOL:
            yaw = 20 if error_x > 0 else -20
            tello.send_rc_control(0, 0, 0, yaw)

        else:
            tello.send_rc_control(0, 15, 0, 0)

# ─── Takeoff ──────────────────────────────────────────────
tello.takeoff()
time.sleep(duration)
tello.send_rc_control(0, 0, 0, 0)
#tello.rotate_clockwise(360)
time.sleep(duration)

# ─── Start Timers ─────────────────────────────────────────
camera_timer = TelloTimer(0.03, stop_event, camera_loop)
flight_timer = TelloTimer(0.1, stop_event, flight_loop)

camera_timer.start()
flight_timer.start()

stop_event.wait()

cv2.destroyAllWindows()
tello.streamoff()
