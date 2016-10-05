import socket
import sys
import time

# Include I/O library for python in PYTHON PATH
galileo_path = "/var/project"
if galileo_path not in sys.path:
    sys.path.append(galileo_path);

from pyGalileo import *

HOST, PORT = "192.168.25.77", 9999
data = "Teste"
TEMP_PIN = A0
LUM_PIN = A1

while (True):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    temperature = analogRead(TEMP_PIN)
    luminosity = analogRead(LUM_PIN)
    n = datetime.datetime.now()
    time = "%02d:%02d:%02d %d/%d/%d" % (n.hour, n.minute, n.second, n.day, n.month, n.year)
    data = "H: %s T: %d L: %d" % (time, temperature, luminosity)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(data)
    finally:
        sock.close()

    time.sleep(5)