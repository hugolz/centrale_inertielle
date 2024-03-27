#!/usr/bin/env python

import flightgear
import listener
import server
import time
import sys
"""
Notes:
    I could add a real logger like the one in https://github.com/bowarc/python_libs
    but it might be overkill
"""


def main():
    listener.start_threaded()

    flightgear.start_threaded()

    server.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

    # Cleanup
    flightgear.stop()
    listener.stop()
