#!/usr/bin/env python

from tornado.options import options, define, parse_command_line
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.wsgi
import tornado.web
import flightgear
import threading
import datetime
import json
import os

CLIENT_FILES_PATH = os.path.dirname(os.path.abspath(__file__)) + "/static"
DISPATCH_TIMEOUT_MS = 400

define('port', type=int, default=8888)


class MainHtml(tornado.web.RequestHandler):
    def get(self):
        self.render(f"{CLIENT_FILES_PATH}\\client.html")


class ClientJs(tornado.web.RequestHandler):
    def get(self):
        with open(f"{CLIENT_FILES_PATH}\\client.js", "r") as f:
            self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
            self.write(f.read())


class ClientCss(tornado.web.RequestHandler):
    def get(self):
        with open(f"{CLIENT_FILES_PATH}\\style.css", "r") as f:
            self.set_header("Content-Type", 'text/css; charset="utf-8"')
            self.write(f.read())


class ClientWS(tornado.websocket.WebSocketHandler):
    # im bored so let's fix this race condition
    client_list_mutex = threading.Lock()
    clients = []

    def check_origin(self, origin):
        return True

    def open(self):
        print(f"[DEBUG] {self.request.remote_ip} connected")

        with ClientWS.client_list_mutex:
            ClientWS.clients.append(self)
            self.report_clients()

    def on_message(self, message):
        print(f"[DEBUG] {self.request.remote_ip} sent:", message)
        msg = json.loads(message)  # todo: safety?
        with ClientWS.client_list_mutex:
            for c in ClientWS.clients:
                if c != self:
                    c.write_message(msg)

    def on_close(self):
        print(f"[INFO] {self.request.remote_ip} has disconnected from server")

        with ClientWS.client_list_mutex:
            ClientWS.clients.remove(self)
            self.report_clients()

    # The asumption for this function is that the mutex has been locked by the calling function
    def report_clients(self):
        print(f"[INFO] Server has currently {len(self.clients)} websockets open")


def dispatch_to_clients():
    # This is not multithreaded, therefore there is no problem having an exec time > DISPATCH_TIMEOUT_MS
    tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(
        00, 00, 00, DISPATCH_TIMEOUT_MS), dispatch_to_clients)

    ClientWS.client_list_mutex.acquire(timeout=DISPATCH_TIMEOUT_MS/60)
    for client in ClientWS.clients:
        client.write_message(json.dumps({
            "event": "fdm",
            "data": {
                "yaw": flightgear.fdm_psi_rad,
                "pitch": flightgear.fdm_theta_rad,
                "roll": flightgear.fdm_phi_rad,
            }
        }))
    ClientWS.client_list_mutex.release()


def start():
    print(f"Running server")
    tornado_app = tornado.web.Application([
        ('/', MainHtml),
        ('/websocket', ClientWS),
        ('/client.js', ClientJs),
        ('/style.css', ClientCss)
    ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    dispatch_to_clients()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start()
