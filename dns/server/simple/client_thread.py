import threading
import socket


class ClientThread(threading.Thread):
    def __init__(self, ip, port, clientsocket, attempt=1):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.client = clientsocket

    def run(self):

        # print("Connection to %s %s" % (self.ip, self.port, ))

        r = self.client.recv(2048)
        print("Recieved the request: ", r)
        try:
            print("IP-Address : ", socket.gethostbyname(r))
        except socket.gaierror:
            print("Could not find IP Address")
        finally:
            # Make sure the socket is closed once we're done with it
            self.client.close()
            return
