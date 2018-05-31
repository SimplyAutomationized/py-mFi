import sys, traceback

try:
    import ujson as json
except ImportError:
    import json

if sys.version_info >= (3,0):
    import asyncio
else:
    import trollius as asyncio

from wss import Client

class UBNTWebSocketClient(Client):
    def __init__(self, ip, port, username, password, loop=asyncio.get_event_loop(), debug = False):
        Client.__init__(self, retry=True, loop=loop)

        self.setTextHandler(self.recv_data)
        self.connectTo(ip, port=port, useSsl=True, url="wss://{}:{}/?username={}&password={}".
                                                  format(ip, port, username, password), protocols=['mfi-protocol'])
        self.debug = debug
        self.ip = ip
        self.port = port

    def onMessage(self, payload):
        pass

    def connected(self):
        pass

    def recv_data(self, payload):
        pass

    def send_cmd(self, data):
        if self.debug:
            print('sending {} to {}'.format(data, self.ip))

        self.sendTextMsg(json.dumps(data))
