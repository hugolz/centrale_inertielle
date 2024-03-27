#!/usr/bin/env python

from tornado.options import options, define, parse_command_line
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.wsgi
import tornado.web
import threading
import json
import os

CLIENT_FILES_PATH = os.path.dirname(os.path.abspath(__file__)) + "\\static"

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
        print(f"[{self.request.remote_ip}] connected")

        with ClientWS.client_list_mutex:
            ClientWS.clients.append(self)
            self.report_clients()

    def on_message(self, message):
        print(f"[{self.request.remote_ip}]:", message)
        msg = json.loads(message)  # todo: safety?

        with ClientWS.client_list_mutex:
            for c in ClientWS.clients:
                if c != self:
                    c.write_message(msg)

    def on_close(self):
        print(f"[{self.request.remote_ip}] disconnected")

        with ClientWS.client_list_mutex:
            ClientWS.clients.remove(self)
            self.report_clients()

    # The asumption for this function is that the mutex has been locked by the calling function
    def report_clients(self):
        print(f"Running {len(self.clients)} clients")


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
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start()
