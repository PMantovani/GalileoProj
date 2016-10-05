import socket
import sys
import time

HOST, PORT = "192.168.25.77", 9999
data = "Teste"

while (True):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(data)
    finally:
        sock.close()

    time.sleep(1)