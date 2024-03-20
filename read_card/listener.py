from pynput.keyboard import Key, Listener, _win32
import copy
KeyCode = _win32.KeyCode

last_pressed = None
running = False


def on_press(key):
    global last_pressed
    last_pressed = key
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
    global running
    print("Listener start")
    running = True
    # Collect events until released
    global listener
    listener = Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

def start_threaded():
    import threading
    threading.Thread(target=start).start()

def stop():
    listener.stop()
