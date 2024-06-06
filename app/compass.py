#!/usr/bin/env python

from app.logger import debug, info, warn, error, critical
from app import serial_reader
import threading
from app import listener
import serial
from app import server
import copy
import time
import json

azimuth = 0
running = False


def listen():
    global azimuth, running
    running = True
    try:
        with serial.Serial(port="/dev/tty.usbmodem101", baudrate=9600, timeout=1, writeTimeout=1) as serial_port2:
            while running:

                last = listener.get_last_key()
                read_data = serial_reader.read_one_compass(serial_port2)
                if last == "esc":
                    break
                if last == "s":
                    print("Save")
                azimuth = read_data

    except Exception as e:
        error(f"Can't access compass data due to: {e}")

    warn("Compass module has exited")
    running = False


def start_threaded():
    global running
    threading.Thread(target=listen).start()
    info("Compass has started")


def stop():
    global running
    running = False
