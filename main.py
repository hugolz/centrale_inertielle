#!/usr/bin/env python

import flightgear_fdm
import flightgear_control
import compass
import listener
import logger
import server
import time
import sys
"""
Notes:
"""


def main():
    # The logger is really not great but it's fine for now
    logger.init_global(custom_exception_hook=True)

    listener.start_threaded()


    compass.start_threaded()

    server.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

    # Cleanup
    flightgear_fdm.stop()
    flightgear_control.stop()
    # compass.stop()
    listener.stop()
