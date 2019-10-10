import json
import logging
import os
import pprint
import time

from http.server import BaseHTTPRequestHandler

from response_handler import ResponseHandler
from automation_handler import AutomationHandler

from projects.mynewt.iutctl import MynewtCtl

routes = {}


def MakeInstrumentationServer(automation_hdl):
    class InstrumentationServer(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.automation_hdl = automation_hdl
            super(InstrumentationServer, self).__init__(*args, **kwargs)

        def do_POST(self):
            content_length = int(
                self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            print("POST request,\nPath: {}\nHeaders:\n{}\n\nBody:\n".format(
                str(self.path), str(self.headers)))
            params = json.loads(post_data.decode('utf-8'))
            pprint.pprint(params)

            # time.sleep(2)
            rsp_hdl = ResponseHandler()
            self.automation_hdl.process(self.path, params, rsp_hdl)

            self.respond({'handler': rsp_hdl})

        def handle_http(self, handler):
            status_code = handler.get_status()

            self.send_response(status_code)

            if status_code is 200:
                content = handler.get_contents()
                self.send_header('Content-type', handler.get_content_type())
            else:
                content = "404 Not Found"

            self.end_headers()

            return bytes(content, 'UTF-8')

        def respond(self, opts):
            response = self.handle_http(opts['handler'])
            self.wfile.write(response)

    return InstrumentationServer
