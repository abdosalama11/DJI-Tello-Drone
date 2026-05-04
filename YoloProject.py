#from ultralytics . utils . plotting import Annotator

#Libraries
###################################
import time , cv2
from ultralytics import YOLO
from threading import Thread
from djitellopy import Tello

#Start of the code
###################################
tello = Tello ()
tello . connect ()
tello . streamon ()

#Variables
###################################
dutration = 2 
speedx = 15
speedy = 0
speedz = 0

#Instructions
###################################
tello.takeoff()
tello.sleep()
tello.send_rc_control( , ,  ,)