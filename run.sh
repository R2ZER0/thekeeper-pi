#!/bin/bash

cd /home/pi/project
source /home/pi/.virtualenvs/cv/bin/activate

export SDL_FBDEV=/dev/fb1
export PYTHONUNBUFFERED=True
python3 test2.py
