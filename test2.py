import os
import pygame
import time
import random
import colorsys

from requests import Session
from threading import Thread

from picamera.array import PiRGBArray
from picamera import PiCamera

import cv2
import numpy as np
from time import sleep

DEBUG = True

#SCREEN_SIZE = (320, 240)
SCREEN_SIZE = (240, 320)
SCREEN_AREA = SCREEN_SIZE[0] * SCREEN_SIZE[1]

# face must take up 1/this'th area of the screen to capture it
FACE_DETECT_DIVIDER = 3

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera(resolution=SCREEN_SIZE, framerate=30)

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


def send_file(filename):
    session = Session()
    url = 'http://fredas-mbp:5050/files' 
    fileh = open(filename, 'rb')
    res = session.post(url, data={}, files={'file': fileh})
    fileh.close()
    os.remove(filename)
    if DEBUG:
        print("Upload Response {}: {}".format(res.status_code, res.text)) 

def send_file_async(filename):
    thread = Thread(target=send_file, args=(filename,))
    thread.start()

run = True
run_count = 0

rawCapture = PiRGBArray(camera, size=SCREEN_SIZE)
#return rawCapture.array

wait_until = time.time()

def calc_colour(n):
    N = 30.0 # Number of frames per full colour cycle
    (r, g, b) = colorsys.hsv_to_rgb((n % N) / N, 1, 0.5)
    return (int(b * 255), int(g * 255), int(r * 255))

def capture_face(img, run_count):
    file_name = "/run/faces/frame_{}.png".format(run_count)
    print("Found Face, saving {}...".format(file_name), end='')
    cv2.imwrite(file_name, img)
    print("Done", time.time() - start)
    
    global wait_until
    wait_until = time.time() + 3.0

    send_file_async(file_name)

def do_frame(start, frame, run_count):
    img = frame.array
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.flip(gray, 0)
    gray = cv2.flip(gray, 1)
    locations = cascade.detectMultiScale(gray, 1.3, 5)


    for (x, y, w, h) in locations:
        if (w * h) >= (SCREEN_AREA/FACE_DETECT_DIVIDER):
            capture_face(img, run_count)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.rectangle(img, (x-4, y-4), (x+w+8, y+h+8), (255, 0, 0), 2)
            cv2.rectangle(img, (x-8, y-8), (x+w+16, y+h+16), (0, 0, 255), 2)
            #cv2.circle(img, ( int(x+w/2), int(y+h/2) ), int((w+h)/3), (0, 0, 255), 3)
        else:
            colour = calc_colour(run_count)
            cv2.circle(img, ( int(x+w/2), int(y+h/2) ), int((w+h)/4), colour, 2)
    

    pgimg = cv2.cvtColor(img ,cv2.COLOR_BGR2RGB)
    pgimg = np.flip(pgimg, 0)
    pgimg = np.flip(pgimg, 1)
    pgimg = pygame.surfarray.make_surface(pgimg)
    screen.blit(pgimg, (0,0))

    pygame.display.update()


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    start = time.time()

    if not (wait_until > start):
        do_frame(start, frame, run_count)

    rawCapture.truncate(0)
    run_count = run_count + 1
