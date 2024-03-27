#!/usr/bin/env python

import flightgear
import listener
import server
import time
import sys


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
