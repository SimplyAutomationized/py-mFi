import trollius as asyncio

try:
    import ujson as json
except ImportError:
    import json

import ssl
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory


class UBNTWebSocketProtocol(WebSocketClientProtocol):
    def onOpen(self):
        print("connected!")
        self.sendMessage(json.dumps({"time": 10}))
        self.factory.client.sendMessage = self.sendMessage
        self.factory.client.connected(None)

class UBNTWebSocketClient(object):
    def __init__(self, ip, port, username, password, loop=None):

        self.__webSocket = WebSocketClientFactory(url="wss://{}:{}/?username={}&password={}".
                                                  format(ip, port, username, password), protocols=['mfi-protocol'])
        self.ip = ip
        self.port = port
        self.callback = None

        self.__webSocket.protocol = UBNTWebSocketProtocol
        self.__webSocket.protocol.onMessage = self.recv_data
        self.__webSocket.protocol.onClose = self.clientConnectionFailed
        self.__webSocket.client = self

        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.loop.run_until_complete(self._connect())

    @asyncio.coroutine
    def _connect(self):
        while True:
            try:
                yield asyncio.From(self.loop.create_connection(self.__webSocket, self.ip, self.port,
                                                               ssl=ssl.SSLContext(ssl.PROTOCOL_SSLv23)))
                return
            except asyncio.py33_exceptions.ConnectionRefusedError:
                print("connection refused")
                yield asyncio.From(asyncio.sleep(5))
                continue

            except OSError:
                print("connection failed")
                yield asyncio.From(asyncio.sleep(5))
                continue

    def connected(self):
        pass

    def recv_data(self, payload, isBinary):
        pass

    def send_cmd(self, data):
        print('sending {}'.format(data))
        self.sendMessage(json.dumps(data))

    def sendMessage(self, data):
        print("Not connected...")
        pass

    def clientConnectionFailed(self, wasClean, code, reason):
        print("Client connection ({}) failed (reason={}.. retrying ..".format(self.ip, reason))
        yield asyncio.From(asyncio.sleep(5))
        self.loop.create_task(self._connect())
