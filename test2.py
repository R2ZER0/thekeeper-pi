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
camera = PiCamera(resolution=(320, 240), framerate=30)

# allow the camera to warpup
sleep(0.1)

# load the cascade for detecting faces. source: TODO
cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

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
        green = (0, 255, 0)
        blue = (0, 0, 255)
        
        self.screen.fill(red) 
        pygame.display.update()

        sleep(0.2)
        self.screen.fill(green) 
        pygame.display.update()

        sleep(0.2)
        self.screen.fill(blue)
        pygame.display.update()
        
        sleep(0.2)

# Create an instance of the PyScope class
scope = pyscope()
scope.test()

screen = scope.screen

run = True
run_count = 0

rawCapture = PiRGBArray(camera, size=(320, 240))
#return rawCapture.array

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    start = time.time()
#    print("\n\nGet Frame {}...".format(run_count), time.time(), ' ', time.time() - start, end=' ')
    #img = get_frame(start)
    img = frame.array
#    print("Done", time.time() - start)

#    print("Convert to Grey...", end='')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#    print("Done", time.time() - start)

#    print("Find Faces...", end='')
    locations = cascade.detectMultiScale(gray, 1.3, 5)
#    print("Done", time.time() - start)
    
    save = False
    for (x, y, w, h) in locations:
        save = True
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    if save:
        print("Found Face, saving...", end='')
        cv2.imwrite("/run/object_locations.bmp", img)
        print("Done", time.time() - start)

#    print("Converting BGR => RGB...", end='')
    pgimg = cv2.cvtColor(img ,cv2.COLOR_BGR2RGB)
#    print("Done", time.time() - start)

#    print("Rotating...", end='')
    pgimg = np.rot90(pgimg)
#    print("Done", time.time() - start)
    #pgimg = pygame.image.load("/run/object_locations.bmp")
    
#    print("Blitting...", end='')
    pgimg = pygame.surfarray.make_surface(pgimg)
    screen.blit(pgimg, (0,0))
#    print("Done", time.time() - start)

#    print("Updating Display...", end='')
    pygame.display.update()
#    print("Done", time.time() - start)

    rawCapture.truncate(0)
    run_count = run_count + 1
