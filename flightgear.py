#!/usr/bin/env python

import serial_reader
import serial
import server
import time
import json

last_fdm = None
running = False


def start():
    global last_fdm

    # The "with" keyword acts as an auto-close for the serial port
    with serial.Serial(
            port="COM6", baudrate=115200, timeout=1, writeTimeout=1) as serial_port:
        # Wait for the board to be ready
        serial_reader.wait_for_init(serial_port)
        while running:
            last_fdm = serial_reader.read_one(serial_port)
    print("Flightgear thread has stopped")


def start_threaded():
    global running
    import threading
    running = True
    threading.Thread(target=start, ).start()


def stop():
    global running
    running = False
