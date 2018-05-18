#!/bin/bash

cd /home/pi
source /home/pi/.virtualenvs/cv/bin/activate
export SDL_FBDEV=/dev/fb1

python test2.py