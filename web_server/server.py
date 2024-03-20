#!/usr/bin/env python

from tornado.options import options, define, parse_command_line
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.websocket
import json
import os

CLIENT_FILES_PATH = os.path.dirname(os.path.abspath(__file__)) + "\\static"

define('port', type=int, default=8888)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(f"{CLIENT_FILES_PATH}\\client.html")


class ClientJS(tornado.web.RequestHandler):
    def get(self):
        with open(f"{CLIENT_FILES_PATH}\\client.js", "r") as f:
            self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
            self.write(f.read())


class ClientCSS(tornado.web.RequestHandler):
    def get(self):
        with open(f"{CLIENT_FILES_PATH}\\style.css", "r") as f:
            self.set_header("Content-Type", 'text/css; charset="utf-8"')
            self.write(f.read())


class MyWebSocket(tornado.websocket.WebSocketHandler):
    clients = []

    def check_origin(self, origin):
        return True

    def open(self):
        print(f"[{self.request.remote_ip}] connected")
        # clients must be accessed through class object!!!
        MyWebSocket.clients.append(self)
        self.report_clients()

    def on_message(self, message):
        print(f"[{self.request.remote_ip}]:", message)
        msg = json.loads(message)  # todo: safety?

        # send other clients this message
        for c in MyWebSocket.clients:
            if c != self:
                c.write_message(msg)

    def on_close(self):
        print(f"[{self.request.remote_ip}] disconnected")
        # clients must be accessed through class object!!!
        MyWebSocket.clients.remove(self)
        self.report_clients()

    def report_clients(self):
        print(f"Running {len(self.clients)} clients")


def main():
    tornado_app = tornado.web.Application([
        ('/', MainHandler),
        ('/websocket', MyWebSocket),
        ('/client.js', ClientJS),
        ('/style.css', ClientCSS)
    ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
