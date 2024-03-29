#!/usr/bin/env python

from logger import debug, info, warn, error, critical


class Data:
    def __init__(self):
        self.ax = 0.
        self.ay = 0.
        self.az = 0.
        self.rx = 0.
        self.ry = 0.
        self.rz = 0.

    def __sub__(self, other):
        new = Data()

        new.ax = self.ax - other.ax
        new.ay = self.ay - other.ay
        new.az = self.az - other.az
        new.rx = self.rx - other.rx
        new.ry = self.ry - other.ry
        new.rz = self.rz - other.rz

        new.ax = round(new.ax, 3)
        new.ay = round(new.ay, 3)
        new.az = round(new.az, 3)
        new.rx = round(new.rx, 3)
        new.ry = round(new.ry, 3)
        new.rz = round(new.rz, 3)

        return new

    def __str__(self):
        return f"Data{{a: {{x: {self.ax}, y: {self.ay}, z: {self.az}}}, r: {{x: {self.rx}, y: {self.ry}, z: {self.rz}}}}}"

    def __eq__(self, other):
        if not isinstance(other, Data):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.ax == other.ax and self.ay == other.ay and self.az == other.az and self.rx == other.rx and self.ry == other.ry and self.rz == other.rz


def parse_float(line: str, trigger: str) -> str:
    s = ""

    index = line.find(trigger)
    if index == -1:
        error(f"Could not parse {trigger}")
        return None

    index += len(trigger) + 2

    while True:
        # check if we're stil reading float characters
        if line[index] not in "1234567890.-":
            break
        s += (line[index])
        index += 1
    return round(float(s), 3)

def parse_int(line : str, trigger: str):
    az = ""

    index = line.find(trigger)
    if index == -1:
        error("Error parsing line in int")
        return None

    index += len(trigger)

    while True:
        # check if we're stil reading int characters
        if line[index] not in "1234567890-":
            break
        s += (line[index])
        index += 1
    return int(s)


def sanitize_line(line_bytes) -> str:
    line = line_bytes.decode('UTF-8')
    return line.replace("\r", "").replace("\n", "")


def wait_for(trigger: str, serial_port):
    while True:
        line = sanitize_line(serial_port.readline())

        if line.startswith(trigger):
            break


def wait_for_init_gy(serial_port):
    wait_for("", serial_port)
    wait_for("Adafruit MPU6050 test!", serial_port)
    wait_for("MPU6050 Found!", serial_port)
    wait_for("Accelerometer range set to:", serial_port)
    wait_for("Gyro range set to:", serial_port)
    wait_for("Filter bandwidth set to:", serial_port)
    wait_for("", serial_port)


def read_one_gy(serial_port) -> Data:
    if not serial_port.isOpen():
        return None

    data = Data()

    while True:
        line = sanitize_line(serial_port.readline())

        if line == "":
            break

        if line.startswith("Acceleration"):
            # debug(f"accel: {line}")

            x = parse_float(line, 'X')
            y = parse_float(line, 'Y')
            z = parse_float(line, 'Z')

            data.ax = x
            data.ay = y
            data.az = z

        elif line.startswith("Rotation"):
            # debug(f"rota: {line}")

            x = parse_float(line, 'X')
            y = parse_float(line, 'Y')
            z = parse_float(line, 'Z')

            data.rx = x
            data.ry = y
            data.rz = z

        elif line.startswith("Temperature"):
            # debug(f"temp: {line}")
            temp = parse_float(line, 'Temperature:')

        else:
            warn(f" serial reader module failled to parse: {line}")

    return data

def read_one_compass(serial_port):
    if not serial_port.isOpen():
        return None
    line = sanitize_line(serial_port.readline())

    if line == "":
        return
    else: 
        return parse_int(line, "A: ")

