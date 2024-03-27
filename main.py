#!/usr/bin/env python

import serial_reader
import flightgear
import listener
import serial
import server
import time
import sys


def main():
    listener.start_threaded()

    # The "with" keyword acts as an auto close
    with serial.Serial(
            port="COM6", baudrate=115200, timeout=1, writeTimeout=1) as serial_port:
        # Wait for the board to be ready
        serial_reader.wait_for("", serial_port)
        serial_reader.wait_for("Adafruit MPU6050 test!", serial_port)
        serial_reader.wait_for("MPU6050 Found!", serial_port)
        serial_reader.wait_for("Accelerometer range set to:", serial_port)
        serial_reader.wait_for("Gyro range set to:", serial_port)
        serial_reader.wait_for("Filter bandwidth set to:", serial_port)
        serial_reader.wait_for("", serial_port)

        flightgear.start_threaded(serial_port)

    server.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

    # Cleanup
    flightgear.stop()
    listener.stop()
