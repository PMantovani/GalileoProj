#!/usr/bin/env python
import SimpleHTTPServer
import SocketServer
import threading
import sys

# Include I/O library for python in PYTHON PATH
galileo_path = ""
if galileo_path not in sys.path:
    sys.path.append(galileo_path);

import pyGalileo


PORT = 8000
TEMP_PIN = 666666
LUM_PIN = 66666666

# Handler used for handling HTTP requests
class PersistentHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

# Thread to update index.html with new sensor readings
def UpdateSensorValues(threading.thread):
    temperature = analogRead(TEMP_PIN)
    luminosity = analogRead(LUM_PIN)

Handler = PersistentHandler
httpd = SocketServer.TCPServer(("", PORT), Handler)

# Defines sensor pins as inputs
pinMode(TEMP_PIN, INPUT)
pinMode(LUM_PIN, INPUT)
# Runs new thread
UpdateSensorValues().start()

print "serving at port", PORT
httpd.serve_forever()