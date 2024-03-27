#!/usr/bin/env python

from flightgear_python.fg_if import FDMConnection
import serial_reader
import threading
import listener
import serial
import server
import copy
import time
import json

fdm_phi_rad = 0.0
fdm_psi_rad = 0.0
fdm_theta_rad = 0.0

running = False


def fdm_callback(fdm_data, event_pipe):
    # global last_fdm

    if event_pipe.child_poll():
        phi_rad_child, psi_rad_child, theta_rad_child, = event_pipe.child_recv()  # unpack tuple
        # set only the data that we need to
        fdm_data['theta_rad'] = theta_rad_child  # we can force our own values
        fdm_data['psi_rad'] = psi_rad_child  # we can force our own values
        fdm_data['phi_rad'] = phi_rad_child  # we can force our own values
        # print("fdm update ")
        # fdm_data.alt_m = fdm_data.alt_m + phi_rad_child  # or just make a relative change

    return fdm_data  # return the whole structure


def start():
    global fdm_phi_rad, fdm_psi_rad, fdm_theta_rad
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

                if last == "esc":
                    break
                elif last == "s":
                    print("Save")
                    base_data = read_data
                    fdm_phi_rad = 0.0
                    fdm_psi_rad = 0.0
                    fdm_theta_rad = 0.0

                data = base_data - read_data
                # print(f"[DEBUG] Received data: {data}")

                # Flightgear
                # phi_rad_parent += data.rz / 10
                # send tuple

                addphi = round(data.rz / 100, 3)*30
                addpsi = round(data.rx / 100, 3)*30
                addtheta = round(data.ry / 100, 3)*30
                fdm_phi_rad += addphi
                fdm_psi_rad += addpsi
                fdm_theta_rad += addtheta
                fdm_event_pipe.parent_send(
                    (fdm_phi_rad, fdm_psi_rad, fdm_theta_rad,))
    except Exception as e:
        print(f"[ERROR] Flightgear module encountered an error: {e}")
    fdm_conn.stop()
    print("[INFO] Flightgear thread has stopped")


def d():
    # global last_fdm
    import time
    while running:
        # print(last_fdm)
        time.sleep(0.1)


def start_threaded():
    global running
    running = True
    threading.Thread(target=start).start()
    threading.Thread(target=d).start()


def stop():
    global running
    running = False
