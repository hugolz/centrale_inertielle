#!/usr/bin/env python

import serial_reader
import server
import time

last_fdm = None
running = False


def start(serial_port):
    while running:
        print("Flightgear lock")
        server.ClientWS.client_list_mutex.acquire()
        print(len(server.ClientWS.clients))
        server.ClientWS.client_list_mutex.release()
        time.sleep(0.5)

    print("Flightgear thread has stopped")


def start_threaded(serial_port):
    global running
    import threading
    running = True
    threading.Thread(target=start, args=(serial_port,)).start()


def stop():
    global running
    running = False
