import trollius as asyncio

try:
    import ujson as json
except ImportError:
    import json

from wss import Client

class UBNTWebSocketClient(Client):
    def __init__(self, ip, port, username, password, loop=asyncio.get_event_loop()):
        Client.__init__(self, retry=True, loop=loop)

        self.setTextHandler(self.recv_data)
        self.connectTo(ip, port=port, useSsl=True, url="wss://{}:{}/?username={}&password={}".
                                                  format(ip, port, username, password), protocols=['mfi-protocol'])
        self.ip = ip
        self.port = port

    def onMessage(self, payload):
        pass

    def connected(self):
        pass

    def recv_data(self, payload):
        pass

    def send_cmd(self, data):
        print('sending {}'.format(data))
        self.sendTextMsg(json.dumps(data))
