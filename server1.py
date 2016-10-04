#!/usr/bin/env python
import SimpleHTTPServer
import SocketServer
import threading
import sys
import datetime

# Include I/O library for python in PYTHON PATH
galileo_path = ""
if galileo_path not in sys.path:
    sys.path.append(galileo_path);

import pyGalileo


PORT = 8000
TEMP_PIN = A0
LUM_PIN = A1

# Handler used for handling HTTP requests
class PersistentHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

# Thread to update index.html with new sensor readings
def UpdateSensorValues(threading.thread):
    temperature = analogRead(TEMP_PIN)
    luminosity = analogRead(LUM_PIN)
    file = open('index_std.html', 'r')
    fileStr = file.read()
    file.close()

    # Get current time
    n = datetime.datetime.now()
    # Format time
    timeStr = "%d:%d:%d %d/%d/%d" % (n.hour, n.minute, n.second, n.day, n.month, n.year)

    # Replace strings in indexRaw.html file to index.html
    fileStr.replace("$hora", timeStr)
    fileStr.replace("$temp", string(temperature))
    fileStr.replace("$lum", string(luminosity))

    # Write changes to index.html
    fileWrite = open("index.html", "w+")
    fileWrite.write(fileStr)
    fileWrite.close()

Handler = PersistentHandler
httpd = SocketServer.TCPServer(("", PORT), Handler)

# Defines sensor pins as inputs
pinMode(TEMP_PIN, INPUT)
pinMode(LUM_PIN, INPUT)
# Runs new thread
UpdateSensorValues().start()

print "serving at port", PORT
httpd.serve_forever()