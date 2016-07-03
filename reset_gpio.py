#!/usr/bin/env python
from RPi import GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIN=25
GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, GPIO.HIGH)
