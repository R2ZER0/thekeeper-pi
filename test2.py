import os
import pygame
import time
import random

from picamera.array import PiRGBArray
from picamera import PiCamera

import cv2
import numpy as np
from time import sleep

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera(resolution=(320, 240))

# allow the camera to warpup
sleep(0.1)

# load the cascade for detecting faces. source: TODO
cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# define function to get current frame of the camera.
def get_frame():
    rawCapture = PiRGBArray(camera)
    camera.capture(rawCapture, format="rgb")
    return rawCapture.array

class pyscope :
    screen = None;
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))
        
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                print("Trying driver ", driver)
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break
    
        if not found:
            raise Exception('No suitable video driver found!')
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print("Framebuffer size: %d x %d" % (size[0], size[1]))
        self.screen = pygame.display.set_mode(size)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def test(self):
        # Fill the screen with red (255, 0, 0)
        red = (255, 0, 0)
        self.screen.fill(red)
        # Update the display
        pygame.display.update()

# Create an instance of the PyScope class
scope = pyscope()
scope.test()
time.sleep(1)

screen = scope.screen

run = True
run_count = 100

while (run):
    img = get_frame()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    locations = cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in locations:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.imwrite("/run/object_locations.bmp", img)
    #buf.write(img.tobytes())

    pgimg = pygame.image.load("/run/object_locations.bmp")
    screen.blit(pgimg, (0,0))

    pygame.display.update()

    run_count = run_count - 1
    if run_count < 0:
        run = True

time.sleep(5)

