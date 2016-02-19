#!/usr/bin/env python
from autobahn.asyncio.websocket import (WebSocketServerProtocol,
                                        WebSocketServerFactory)
import socket
from timeout import timeout, TimeoutError


class MyServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            try:
                with timeout(seconds=3):
                    payload = socket.gethostbyname(payload.decode('utf8'))
            except socket.gaierror:
                payload = "Could not find IP Address"
            except TimeoutError:
                payload = "Timeout"
            print("IP-Address : ", payload)

        # echo back message verbatim
        self.sendMessage(payload.encode("utf8"), isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000", debug=False)
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
