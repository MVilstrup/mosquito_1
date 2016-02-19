#!/usr/bin/env python
from autobahn.asyncio.websocket import (WebSocketClientProtocol,
                                        WebSocketClientFactory)

import asyncio


class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    @asyncio.coroutine
    def onOpen(self):
        print("WebSocket connection open.")

        # start sending messages every second ..
        count = 0
        while True:
            self.sendMessage(u"domain{}.com".format(count).encode('utf8'), isBinary=False)
            count += 1
            # self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
            yield from asyncio.sleep(1)

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    factory = WebSocketClientFactory(u"ws://127.0.0.1:9000", debug=False)
    factory.protocol = MyClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        coro.stop()
    finally:
        loop.close()
