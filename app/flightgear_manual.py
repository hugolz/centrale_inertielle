#!/usr/bin/env python

from app.logger import debug, info, warn, error, critical
from flightgear_python.fg_if import FDMConnection
from app import serial_reader
from app import flightgear
from app import listener
from app import server
import threading
import serial
import math
import copy
import time
import json


fdm_psi_rad = 0.0
fdm_theta_rad = 0.0
fdm_phi_rad = 0.0

running = False
"""
Flightgear startup options
    --native-fdm=socket,out,30,localhost,5501,udp --native-fdm=socket,in,30,localhost,5502,udp --max-fps=30 --altitude=3000
"""


def fdm_callback(fdm_data, event_pipe):
    # global last_fdm
    if event_pipe.child_poll():
        _ = event_pipe.child_recv()  # no data wanted

    with open("cache", "w") as f:
        f.write(f"{(-fdm_data['psi_rad'] + math.pi) % (math.pi * 2.) - math.pi} {fdm_data['theta_rad']} {-fdm_data['phi_rad']}")

    # print(f"Updating callback.. {fdm_data['psi_rad']}, {fdm_data['theta_rad']}, {fdm_data['phi_rad']}")

    return None


def start():
    global fdm_psi_rad, fdm_theta_rad, fdm_phi_rad, running
    running = True

    base_data = serial_reader.Data()

    fdm_conn = FDMConnection(fdm_version=24)
    fdm_event_pipe = fdm_conn.connect_rx('localhost', 5501, fdm_callback)
    fdm_conn.connect_tx('localhost', 5502)
    fdm_conn.start()  # Start the FDM RX/TX loop

    try:
        while running:
            try:
                with open("cache", "r") as f:
                    content = f.read()
                    splitted = content.split(" ")
                    if len(splitted) != 3:
                        # Read error, probably caused by concurency between threads, a mutex could be used to fix it
                        continue
                    fdm_psi_rad = splitted[0]
                    fdm_theta_rad = splitted[1]
                    fdm_phi_rad = splitted[2]
            except IOError as e:
                warn(f"Cache reset due to: {e}")
                with open("cache", "w") as f:
                    f.write("0 0 0")
            except Exception as e:
                warn(f"Could not read the cache due to: {e}")

            fdm_event_pipe.parent_send((0,))

    except Exception as e:
        warn(f"FlightgearMANUAL module encountered an error: {e}")
    fdm_conn.stop()
    stop()
    warn("FlightgearMANUAL thread has stopped")
    running = False


def start_threaded():
    global running
    running = True
    threading.Thread(target=start).start()
    info("FlightgearMANUAL module has started")


def stop():
    global running
    running = False
    flightgear.stop()


if __name__ == "__main__":
    import logger
    logger.init_global()
    start()


def stop():
    global running
    running = False
    flightgear.stop()


if __name__ == "__main__":
    import logger
    logger.init_global()
    start()
