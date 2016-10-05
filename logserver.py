import SocketServer

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data

        with open("log.txt", "a") as file:
            file.write(self.data)

if __name__ == "__main__":
    HOST, PORT = "", 4444

    # Create the server, binding to localhost on port 4444
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()