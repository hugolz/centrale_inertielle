#!/usr/bin/env python

from tornado.options import options, define, parse_command_line
from logger import debug, info, warn, error, critical
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.wsgi
import tornado.web
import flightgear_fdm
import flightgear_control
import compass
import threading
import datetime
import json
import os

CLIENT_FILES_PATH = os.path.dirname(os.path.abspath(__file__)) + "/static"
DISPATCH_TIMEOUT_MS = 100
state =""


define('port', type=int, default=8888)


class MainHtml(tornado.web.RequestHandler):
    display_page = "index.html" 
    def get(self):
        self.render(f"{CLIENT_FILES_PATH}/{MainHtml.display_page}")


class ClientJs(tornado.web.RequestHandler):
    def get(self):
        with open(f"{CLIENT_FILES_PATH}/client.js", "r") as f:
            self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
            self.write(f.read())
            
class PostHandler(tornado.web.RequestHandler):        
    
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
                print(f"[ERROR] Couldn't read valid state for state : {data['state']}")
        MainHtml.display_page = "/client.html"



class ClientCss(tornado.web.RequestHandler):
    def get(self):
        with open(f"{CLIENT_FILES_PATH}/style.css", "r") as f:
            self.set_header("Content-Type", 'text/css; charset="utf-8"')
            self.write(f.read())


class ClientWS(tornado.websocket.WebSocketHandler):
    clients = []
    

    def check_origin(self, origin):
        return True

    def open(self):
        debug(f"{self.request.remote_ip} connected")

        ClientWS.clients.append(self)
        self.report_clients()

    def on_message(self, message):
        debug(f"{self.request.remote_ip} sent: {message}")
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


def dispatch_to_clients():
    global state
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
                warn(f"[ERROR] Couldn't send proper data to client with STATE : {state}")
    


def start():
    print(f"Running server")
    tornado_app = tornado.web.Application([
        ('/', MainHtml),
        ('/websocket', ClientWS),
        ('/client.js', ClientJs),
        ('/server.py', PostHandler),
        ('/style.css', ClientCss)
    ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    dispatch_to_clients()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start()
