#!/usr/bin/env python
import SimpleHTTPServer
import SocketServer
from threading import Thread
import sys
import datetime

# Include I/O library for python in PYTHON PATH
galileo_path = "/var/project"
if galileo_path not in sys.path:
    sys.path.append(galileo_path);

from pyGalileo import *


PORT = 8000
TEMP_PIN = A0
LUM_PIN = A1

# Handler used for handling HTTP requests
class PersistentHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

# Thread to update index.html with new sensor readings
class UpdateSensorValues(Thread):
    def run(self):
        while (True):
            temperature = analogRead(TEMP_PIN)
            luminosity = analogRead(LUM_PIN)
            file = open('index_std.html', 'r')
            fileStr = file.read()
            file.close()

            # Get current time
            n = datetime.datetime.now()
            # Format time
            timeStr = "%2.d:%2.d:%2.d %d/%d/%d" % (n.hour, n.minute, n.second, n.day, n.month, n.year)

            # Replace strings in indexRaw.html file to index.html
            fileStr = fileStr.replace("$hora", timeStr)
            fileStr = fileStr.replace("$temp", str(temperature))
            fileStr = fileStr.replace("$lum", str(luminosity))

            # Write changes to index.html
            fileWrite = open("index.html", "w+")
            fileWrite.write(fileStr)
            fileWrite.close()

            # delay for update
            delay(5000)

Handler = PersistentHandler
httpd = SocketServer.TCPServer(("", PORT), Handler)
httpd.allow_reuse_address = True

# Runs new thread
UpdateSensorValues().start()

print "serving at port", PORT
httpd.serve_forever()