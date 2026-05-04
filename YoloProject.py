#Libraries
###################################
import time , cv2
from ultralytics import YOLO
from ultralytics . utils . plotting import Annotator
from threading import Thread
from djitellopy import Tello
#Start of the code
###################################
tello = Tello ()
tello . connect ()
tello . streamon ()
keepRecording = True
YOLO_Model = YOLO("yolo26n.pt")
frame_read = tello . get_frame_read ()
#Variables
###################################
dutration = 2 #sec
class_ID = 39
Found_Target = False
Safe_Area = 220000
CENTER_TOL = 50 


#Instructions
###################################

#Take off and hovering + searching by rotation
tello.takeoff()
time.sleep(dutration)
tello.send_rc_control( 0,0,0,0)
tello.rotate_clockwise(360)
time.sleep(dutration)
while True:

  
# Search pattern
    if Found_Target == False:
        #VAR
        speed = 10;# cm/s
        rotation = 90;# degrees
        for i in range(20):
            frame = frame_read.frame
            vid = frame.copy()
        # Run YOLO detection
            results = YOLO_Model.predict(vid, classes = [class_ID])
            annotator = Annotator(vid, line_width=2, font_size=10)
            cv2.imshow("Results", annotator.result())
            cv2.waitKey(1)
        #condition of founding the object
            if len(results[0].boxes) > 0:
                Found_Target = True
                break
            
            #Instructions
            tello.send_rc_control( 0,speed,0,0)
            time.sleep(dutration)
            tello.rotate_clockwise(rotation)
            time.sleep(dutration)
            tello.rotate_counter_clockwise(rotation)
            time.sleep(dutration)
            tello.rotate_clockwise(rotation)
            time.sleep(dutration)
            tello.rotate_counter_clockwise(rotation)
            time.sleep(dutration)
            tello.send_rc_control( 0,speed,0,0)
            time.sleep(dutration)
    
     
    else:
        frame = frame_read.frame
        vid = frame.copy()
        results = YOLO_Model.predict(vid, classes=[class_ID])
        annotator = Annotator(vid, line_width=2, font_size=10)
        Area= 0
        frame_center_x = vid.shape[1] / 2
        error_x = 0
        for obj in results:
            boxes = obj.boxes
            for box in boxes:
                label = YOLO_Model.names[int(box.cls)] + " ( " + str(round(float(box.conf[0]), 2)) + " ) "
                annotator.box_label(box.xyxy[0], label)
                print(box.xyxy[0])
                x_D = abs(int(box.xyxy[0][0]) - int(box.xyxy[0][2]))
                y_D = abs(int(box.xyxy[0][1]) - int(box.xyxy[0][3]))
                Area = x_D * y_D
                object_center_x = (box.xyxy[0][0] + box.xyxy[0][2]) / 2
                error_x = object_center_x - frame_center_x

                print(f"Area: {Area} | error_x: {error_x:.1f}")
        
        if Area >= Safe_Area:
                    tello.send_rc_control(0, 0, 0, 0)
                    time.sleep(dutration    )
                    tello.land()
                    cv2.destroyAllWindows()
                    tello.streamoff()
                    exit()
        # Not centered — rotate first
        elif abs(error_x) > CENTER_TOL:
                    yaw = -20 if error_x > 0 else 20 # can be yaw = 20 if error_x > 0 else -20 
                    tello.send_rc_control(0, 0, 0, yaw)

        # Centered — move forward
        else:
                    tello.send_rc_control(0, 15, 0, 0)       
        
    cv2.imshow("Results", annotator.result())
    cv2.waitKey(1)
        

cv2.destroyAllWindows()
tello.streamoff()


#cv2.destroyAllWindows()
#tello.streamoff()
#recorder = Thread ( target = videoRecorder )
#recorder . start ()
#time . sleep (5.0)
#keepRecording = False
#recorder . join ()            
