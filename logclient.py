import socket
import sys

HOST, PORT = "192.168.25.77", 4444
data = "Teste"

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    while (True):
        sock.sendall(data + "\n")
        delay(10000)
finally:
    sock.close()