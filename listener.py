#!/usr/bin/env python

from pynput.keyboard import Key, Listener, _win32
import copy
KeyCode = _win32.KeyCode

last_pressed = None
running = False
listener = None


def on_press(key):
    global last_pressed
    last_pressed = key

    # The default format is weird, let's use strings without type identifier
    if type(key) == Key:
        last_pressed = f"{key}".replace("Key.", "")
    else:
        last_pressed = f"{key}".replace("'", "")
    # print(f'{last_pressed} pressed'.format(key))
    return running


def on_release(key):
    return running


def get_last_key():
    global last_pressed
    if last_pressed == None:
        return None
    e = copy.deepcopy(last_pressed)
    last_pressed = None
    return e


def start():
    global listener, running
    running = True
    listener = Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    print("Listener start")


def start_threaded():
    import threading
    threading.Thread(target=start).start()


def stop():
    global listener
    listener.stop()
    print("Listener has been stopped")
