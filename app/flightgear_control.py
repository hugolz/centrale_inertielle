#!/usr/bin/python3
"""
Simple Controls example that sweeps the control surfaces and periodically puts the gear up/down
"""
import time
import math
from flightgear_python.fg_if import CtrlsConnection
from app.logger import debug, info, warn, error, critical
import serial
import threading
from app import serial_reader
from app import listener
from app import flightgear

gear_down_child_state = True
running = False

fdm_psi_rad = 0.0
fdm_theta_rad = 0.0
fdm_phi_rad = 0.0

"""
Flightgear startup options
    --native-ctrls=socket,out,30,localhost,5503,udp --native-ctrls=socket,in,30,localhost,5504,udp --altitude=3000
"""


def ctrls_callback(ctrls_data, event_pipe):

    if event_pipe.child_poll():
        gear_down_child, data, = event_pipe.child_recv()  # unpack tuple
        # TODO: FG sometimes ignores "once" updates? i.e. if we set `ctrls_data.gear_handle`
        #  the next callback will still have the old value of `ctrls_data.gear_handle`, not
        #  the one that we set. To fix this we can just keep our own state of what the value
        #  should be and set it every time. I still need to figure out a clean way to fix
        #  this on the backend

        gear_down_child_state = gear_down_child

        sensibility = 0.1
        ctrls_data.aileron = data.rz * sensibility
        ctrls_data.elevator = -data.ry * sensibility
        ctrls_data.rudder = data.rx * sensibility
    # ctrls_data.gear_handle = 'down' if gear_down_child_state else 'up'

    # print(ctrls_data)
    # set only the data that we need to
    # ctrls_data.aileron = math.sin(time.time())
    # ctrls_data.elevator = math.sin(time.time())
    # ctrls_data.rudder = math.sin(time.time())
    # ctrls_data.throttle[0] = (math.sin(time.time()) / 2) + 0.5
    # ctrls_data.throttle[1] = (-math.sin(time.time()) / 2) + 0.5
    ctrls_data.throttle[0] = 1
    # ctrls_data.throttle[1] = 1
    return ctrls_data  # return the whole structure


def start():
    global fdm_psi_rad, fdm_theta_rad, fdm_phi_rad, gear_down_child_state

    flightgear.start(["--native-ctrls=socket,out,30,localhost,5503,udp",
                      "--native-ctrls=socket,in,30,localhost,5504,udp",
                      "--altitude=3000"])

    ctrls_conn = CtrlsConnection(ctrls_version=27)
    ctrls_event_pipe = ctrls_conn.connect_rx('localhost', 5503, ctrls_callback)
    ctrls_conn.connect_tx('localhost', 5504)
    ctrls_conn.start()  # Start the Ctrls RX/TX loop

    base_data = serial_reader.Data()

    accumulated_data = serial_reader.Data()

    gear_down_parent = True
    time.sleep(2)
    try:
        with serial.Serial(port="/dev/tty.usbmodem101", baudrate=115200, timeout=1, writeTimeout=1) as serial_port:
            serial_reader.wait_for_init_gy(serial_port)
            while running:

                last = listener.get_last_key()
                read_data = serial_reader.read_one_gy(serial_port)
                # if last == "esc":
                # break
                if last == "s":
                    print("Save")
                    base_data = read_data
                    accumulated_data = serial_reader.Data()

                data = base_data - read_data
                # debug(f"{fdm_psi_rad},{fdm_theta_rad},{fdm_phi_rad}")
                debug(f"Received data: {data}")

                precision = 100
                addpsi = round(data.rx / precision, 3) * precision
                addtheta = round(data.ry / precision, 3) * precision
                addphi = round(data.rz / precision, 3) * precision

                sensibility_fdm = 0.3
                fdm_psi_rad += -addpsi * sensibility_fdm
                fdm_theta_rad += addtheta * sensibility_fdm
                fdm_phi_rad += addphi * sensibility_fdm

                accumulated_data += data

                # could also do `ctrls_conn.event_pipe.parent_send` so you just need to pass around `ctrls_conn`
                ctrls_event_pipe.parent_send(
                    (gear_down_parent, accumulated_data,))  # send tuple
                # gear_down_parent = not gear_down_parent  # Flip gear state
                # time.sleep(5)
    except Exception as e:
        error(f"FlightgearCTRL module encountered an error: {e}")
    ctrls_conn.stop()
    stop()

    warn(f"FlightgearCTRL module has stopped")
    running = False


def start_threaded():
    global running
    running = True
    threading.Thread(target=start).start()
    info("FlightgearCTRL module has started")


def stop():
    global running
    running = False
    flightgear.stop()


if __name__ == '__main__':  # NOTE: This is REQUIRED on Windows
    import logger
    logger.init_global()

    listener.start_threaded()

    running = True
    start()
