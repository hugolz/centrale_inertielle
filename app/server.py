#!/usr/bin/env python

from tornado.options import options, define, parse_command_line
from app.logger import trace, debug, info, warn, error, critical
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.wsgi
import tornado.web
from app import flightgear_fdm
from app import flightgear_control
from app import flightgear_manual
from app import compass
from app import flightgear
import threading
import datetime
import enum
import json
import os


class State(enum.Enum):
    MAIN = 0
    PILOT = 1
    INERTIAL = 2
    MANUAL = 3


CLIENT_FILES_PATH = os.path.dirname(os.path.abspath(__file__)) + "/static"
DISPATCH_TIMEOUT_MS = 100
PORT = 8888
state = State.MAIN
running = False


define('port', type=int, default=PORT)


class MainHtml(tornado.web.RequestHandler):
    def get(self):
        if state == State.MAIN:
            self.render(f"{CLIENT_FILES_PATH}/index.html")
        elif state == State.INERTIAL or state == State.PILOT:
            self.render(f"{CLIENT_FILES_PATH}/module_interface.html")
        else:
            self.render(f"{CLIENT_FILES_PATH}/manual_interface.html")

    def post(self):
        global state
        data = tornado.escape.json_decode(self.request.body)
        new_state = data["state"]
        try:
            state = State[new_state.upper()]
        except Exception as e:
            error(f"Could not understand received new state: {new_state}")

        self.write(new_state)

        if state == State.PILOT:
            flightgear_control.start_threaded()
        elif state == State.INERTIAL:
            flightgear_fdm.start_threaded()
        elif state == State.MANUAL:
            flightgear_manual.start_threaded()


class ClientJs(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
        self.render(f"{CLIENT_FILES_PATH}/client.js")


class ControlsJs(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
        self.render(f"{CLIENT_FILES_PATH}/controls.js")


class WebsocketJs(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
        self.render(f"{CLIENT_FILES_PATH}/websocket.js")


class ClientCss(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", 'text/css; charset="utf-8"')
        self.render(f"{CLIENT_FILES_PATH}/style.css")


class ClientWS(tornado.websocket.WebSocketHandler):
    clients = []

    def check_origin(self, origin):
        return True

    def open(self):
        debug(f"{self.request.remote_ip} connected")

        ClientWS.clients.append(self)
        self.report_clients()

    def on_message(self, message):
        # debug(f"{self.request.remote_ip} sent: {message}")
        msg = json.loads(message)  # todo: safety?
        for c in ClientWS.clients:
            if c != self:
                c.write_message(msg)

    def on_close(self):
        info(f"{self.request.remote_ip} has disconnected from server")

        ClientWS.clients.remove(self)
        self.report_clients()

    # The asumption for this function is that the mutex has been locked by the calling function

    def report_clients(self):
        info(f"Server has currently {len(self.clients)} websockets open")
        pass


class Flightgear(tornado.web.RequestHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        command = data["command"].lower()

        if command == "start":
            yaw = data["yaw"]
            pitch = data["pitch"]
            roll = data["roll"]
            vc = data["vc"]
            debug(f"yaw: {yaw}, pitch: {pitch}, roll: {roll}")
            flightgear.start(["--native-fdm=socket,out,30,localhost,5501,udp",
                              "--native-fdm=socket,in,30,localhost,5502,udp",
                              "--max-fps=30", "--altitude=3000",
                              f"--heading={yaw}", f"--roll={pitch}", f"--pitch={roll}", f"--vc={vc}"])
            self.write("Ok")
        elif command == "stop":
            flightgear.stop()
            self.write("Ok")
        else:
            warn(f"Unknown command: {command}")
            self.write("Unknown command")


# Collect data from sensor / command input & sends them to the clientS


def dispatch_to_clients():
    global state, running
    if not running:  # I don't think this is usefull as tornado cannot execute timeouts when stopped
        info("Exiting server dispatch loop")
        return

    # This is not multithreaded, therefore there is no problem having an exec time > DISPATCH_TIMEOUT_MS
    tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(
        00, 00, 00, DISPATCH_TIMEOUT_MS), dispatch_to_clients)

    if state == State.MAIN:
        return  # Nothing to do, exit
    elif state == State.PILOT:
        for client in ClientWS.clients:
            client.write_message(json.dumps({
                "event": "fdm",
                "data": {
                    "yaw": flightgear_control.fdm_psi_rad,
                    "pitch": flightgear_control.fdm_theta_rad,
                    "roll": flightgear_control.fdm_phi_rad,
                    "azimuth": compass.azimuth,
                }
            }))
    elif state == State.INERTIAL:
        for client in ClientWS.clients:
            client.write_message(json.dumps({
                "event": "fdm",
                "data": {
                    "yaw": flightgear_fdm.fdm_psi_rad,
                    "pitch": flightgear_fdm.fdm_theta_rad,
                    "roll": flightgear_fdm.fdm_phi_rad,
                    "azimuth": compass.azimuth,
                }
            }))
    elif state == State.MANUAL and flightgear.process != None:
        fdm_psi_rad = 0
        fdm_theta_rad = 0
        fdm_phi_rad = 0

        try:
            with open("cache", "r") as f:
                content = f.read()
                splitted = content.split(" ")
                fdm_psi_rad = splitted[0]
                fdm_theta_rad = splitted[1]
                fdm_phi_rad = splitted[2]
        except Exception as e:
            with open("cache", "w") as f:
                f.write("0 0 0")

        debug(f"Sending {fdm_psi_rad}, {fdm_theta_rad}, {fdm_phi_rad}")
        for client in ClientWS.clients:
            client.write_message(json.dumps({
                "event": "fdm",
                "data": {
                    "yaw": fdm_psi_rad,
                    "pitch": fdm_theta_rad,
                    "roll": fdm_phi_rad,
                    "azimuth": compass.azimuth,
                }
            }))


def start():
    global running
    info(f"Running server at {PORT} w/ files at: {CLIENT_FILES_PATH}")
    tornado_app = tornado.web.Application([
        ('/', MainHtml),
        ('/websocket', ClientWS),
        ('/client.js', ClientJs),
        ('/style.css', ClientCss),
        ('/controls.js', ControlsJs),
        ('/websocket.js', WebsocketJs),
        ('/flightgear', Flightgear),
    ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    running = True
    dispatch_to_clients()

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        info("Server KeyboardInterrupt")
        pass
    running = False
    warn(f"Server has stopped")


def stop():
    global running
    running = False


if __name__ == '__main__':
    start()
