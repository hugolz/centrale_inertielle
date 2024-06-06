#!/usr/bin/env python

from app import flightgear_fdm
from app import flightgear_control
from app import compass
from app import listener
from app import logger
from app import server
import time
import sys


"""
Notes:
"""


def main():
    # The logger is really not great but it's fine for now
    logger.init_global(custom_exception_hook=True)

    listener.start_threaded()
    while not listener.running:
        pass

    compass.start_threaded()
    while not compass.running:
        pass

    server.start()  # Blocking


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        info("Main KeyboardInterrupt")
        pass
    # Cleanup
    flightgear_fdm.stop()
    flightgear_control.stop()
    compass.stop()
    listener.stop()
