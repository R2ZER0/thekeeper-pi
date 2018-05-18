from picamera.array import PiRGBArray
from picamera import PiCamera

import cv2
import numpy as np
from time import sleep

buf = open("/dev/fb1", "wb")

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()

# allow the camera to warpup
sleep(0.1)

# load the cascade for detecting faces. source: TODO
cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# define function to get current frame of the camera.
def get_frame():
    rawCapture = PiRGBArray(camera)
    camera.capture(rawCapture, format="rgb")
    return rawCapture.array

run = True

while (run):
    img = get_frame()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    locations = cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in locations:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    #cv2.imwrite("object_locations.png", img)
    buf.write(img.tobytes())
    run = False

