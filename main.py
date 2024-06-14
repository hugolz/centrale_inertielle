#!/usr/bin/env python

from app import flightgear_fdm
from app import flightgear_control
from app import compass
from app import listener
from app import logger
from app import server
import time
import sys
from app import flightgear

"""
Notes:


"""
# flightgear.start(["--native-fdm=socket,out,30,localhost,5501,udp",
#                   "--native-fdm=socket,in,30,localhost,5502,udp", "--fdm=null", "--altitude=3000"])
# while True:
#     pass
# sys.exit(0)


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
        logger.info("Main KeyboardInterrupt")
        pass
    # Cleanup
    flightgear_fdm.stop()
    flightgear_control.stop()
    compass.stop()
    flightgear.stop()
    listener.stop()
