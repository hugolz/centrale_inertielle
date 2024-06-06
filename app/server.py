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
from app import compass
import threading
import datetime
import json
import os

CLIENT_FILES_PATH = os.path.dirname(os.path.abspath(__file__)) + "/static"
DISPATCH_TIMEOUT_MS = 100
PORT = 8888
state = ""
running = False


define('port', type=int, default=PORT)


class MainHtml(tornado.web.RequestHandler):
    display_page = "index.html"

    def get(self):
        self.render(f"{CLIENT_FILES_PATH}/{self.display_page}")

    def post(self):
        global state
        data = tornado.escape.json_decode(self.request.body)
        state = data["state"]
        self.write(state)

        match state:
            case "pilot":
                flightgear_control.start_threaded()
            case "inertial":
                flightgear_fdm.start_threaded()
            case "":
                pass
            case _:
                error(f"Couldn't read valid state for state : {data['state']}")
        MainHtml.display_page = "/client.html"


class ClientJs(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
        self.render(f"{CLIENT_FILES_PATH}/client.js")


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


# Collect data from sensor / command input & sends them to the clientS
def dispatch_to_clients():
    global state, running
    if not running:  # I don't think this is usefull as tornado cannot execute timeouts when stopped
        info("Exiting server dispatch loop")
        return

    # This is not multithreaded, therefore there is no problem having an exec time > DISPATCH_TIMEOUT_MS
    tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(
        00, 00, 00, DISPATCH_TIMEOUT_MS), dispatch_to_clients)

    match state:
        case "pilot":

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

        case "inertial":
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

        case "":
            pass

        case _:
            error(f"Couldn't send proper data to client with STATE: {state}")


def start():
    global running
    info(f"Running server at {PORT} w/ files at: {CLIENT_FILES_PATH}")
    tornado_app = tornado.web.Application([
        ('/', MainHtml),
        ('/websocket', ClientWS),
        ('/client.js', ClientJs),
        ('/style.css', ClientCss)
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
