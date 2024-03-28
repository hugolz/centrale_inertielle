#!/usr/bin/env python

from logger import debug, info, warn, error, critical
from flightgear_python.fg_if import FDMConnection
import serial_reader
import threading
import listener
import serial
import server
import copy
import time
import json

fdm_psi_rad = 0.0
fdm_theta_rad = 0.0
fdm_phi_rad = 0.0

running = False


def fdm_callback(fdm_data, event_pipe):
    # global last_fdm

    if event_pipe.child_poll():
        psi_rad_child, theta_rad_child, phi_rad_child, = event_pipe.child_recv()  # unpack tuple
        # set only the data that we need to
        fdm_data['psi_rad'] = psi_rad_child
        fdm_data['theta_rad'] = theta_rad_child
        fdm_data['phi_rad'] = phi_rad_child

    return fdm_data


def start():
    global fdm_psi_rad, fdm_theta_rad, fdm_phi_rad
    base_data = serial_reader.Data()

    fdm_conn = FDMConnection(fdm_version=24)
    fdm_event_pipe = fdm_conn.connect_rx('localhost', 5501, fdm_callback)
    fdm_conn.connect_tx('localhost', 5502)
    fdm_conn.start()  # Start the FDM RX/TX loop

    try:
        with serial.Serial(port="COM6", baudrate=115200, timeout=1, writeTimeout=1) as serial_port:
            serial_reader.wait_for_init(serial_port)
            while running:

                last = listener.get_last_key()
                read_data = serial_reader.read_one(serial_port)
                # if last == "esc":
                # break
                if last == "s":
                    print("Save")
                    base_data = read_data
                    fdm_psi_rad = 0.0
                    fdm_theta_rad = 0.0
                    fdm_phi_rad = 0.0

                data = base_data - read_data
                # debug(f"{fdm_psi_rad},{fdm_theta_rad},{fdm_phi_rad}")
                # debug(f"Received data: {data}")

                precision = 100
                addpsi = round(data.rx / precision, 3) * precision
                addtheta = round(data.ry / precision, 3) * precision
                addphi = round(data.rz / precision, 3) * precision

                sensibility = 0.3
                fdm_psi_rad += -addpsi * sensibility
                fdm_theta_rad += addtheta * sensibility
                fdm_phi_rad += addphi * sensibility
                fdm_event_pipe.parent_send(
                    (fdm_psi_rad, fdm_theta_rad, fdm_phi_rad,))
    except Exception as e:
        error(f"Flightgear module encountered an error: {e}")
    fdm_conn.stop()
    info("Flightgear thread has stopped")


def start_threaded():
    global running
    running = True
    threading.Thread(target=start).start()


def stop():
    global running
    running = False
