#!/usr/bin/env python

from logger import debug, info, warn, error, critical
import serial_reader
import threading
import listener
import serial
import server
import copy
import time
import json

azimuth = 0

def listen():
    global azimuth
    try:
        with serial.Serial(port="/dev/tty.usbmodem101", baudrate=9600, timeout=1, writeTimeout=1) as serial_port2:
            while running:

                #last = listener.get_last_key()
                read_data = serial_reader.read_one_compass(serial_port2)
                # if last == "esc":
                # break
                #if last == "s":
                   # print("Save")
                azimuth = read_data
                
    except Exception as e:
        error(f"Compass data couldn't been read : {e}")

def start_threaded():
    global running
    running = True
    threading.Thread(target=listen).start()


def stop():
    global running
    running = False

