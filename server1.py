#!/usr/bin/env python
import SimpleHTTPServer
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import sys
import datetime

# Include I/O library for python in PYTHON PATH
galileo_path = "/var/project"
if galileo_path not in sys.path:
    sys.path.append(galileo_path);

from pyGalileo import *


PORT = 80
TEMP_PIN = A0
LUM_PIN = A1

# Handler used for handling HTTP requests
class PersistentHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    pass

# Thread to update index.html with new sensor readings
class UpdateSensorValues(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.kill_received = False

    def run(self):
        while (not self.kill_received):
            temperature = analogRead(TEMP_PIN)
            luminosity = analogRead(LUM_PIN)
            file = open('index_std.html', 'r')
            fileStr = file.read()
            file.close()

            # Get current time
            n = datetime.datetime.now()
            # Format time
            timeStr = "%02d:%02d:%02d %d/%d/%d" % (n.hour, n.minute, n.second, n.day, n.month, n.year)

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

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    # Handles requests in a separate thread.
    pass

if __name__ == "__main__":
    Handler = PersistentHandler
    httpd = ThreadedHTTPServer(("", PORT), Handler)
    httpd.allow_reuse_address = True

    # Runs new thread
    threadSensor = UpdateSensorValues()
    threadSensor.start()

    print "serving at port", PORT
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        threadSensor.kill_received = True
    httpd.server_close()
    print "Server killed"
