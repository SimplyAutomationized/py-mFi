import ssl, time
import ujson as json
import requests
import trollius as asyncio
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from mPower import *


class MFiRest:
    def __init__(self, ip, username, password):
        self.label = ''
        self.ip = ip
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.url = "https://{}/".format(ip)
        self.session.verify = False
        self.session.get(self.url)
        post_data = {"uri": "/", "username": self.username, "password": self.password}
        self.session.post((self.url + "/login.cgi"), headers={"Expect": ""},
                          data=post_data, allow_redirects=True)
        data = (self.session.get((self.url + "/mfi/sensors.cgi"))).json()
        for key in data['sensors'][0].keys():
            setattr(self, key, data['sensors'][0][key])


class UbntWebSocketProtocol(WebSocketClientProtocol):
    def onOpen(self):
        self.factory.client.sendMessage = self.sendMessage


class UBNTWebSocketClient:
    def __init__(self, ip, port, username, password, loop=None):

        self.__webSocket = WebSocketClientFactory(url="wss://{}:{}/?username={}&password={}".
                                                  format(ip, port, username, password), protocols=['mfi-protocol'])
        self.ip = ip
        self.port = port
        self.callback = None

        self.__webSocket.protocol = UbntWebSocketProtocol
        self.__webSocket.protocol.onMessage = self.recv_data
        self.__webSocket.protocol.onClose = self.clientConnectionFailed
        self.__webSocket.client = self

        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.loop.create_task(self._connect())

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
        self.sendMessage(json.dumps(data))

    def sendMessage(self, data):
        pass

    def clientConnectionFailed(self, wasClean, code, reason):
        print("Client connection failed .. retrying ..")
        self.loop.create_task(self._connect())


class MSwitch(MPower, UBNTWebSocketClient, MFiRest):
    _dimmer_level = 0
    _output = 0
    status = {}

    def __init__(self, ip, port, username, password):
        MPower.__init__(self)
        self.label = 'Room'
        MFiRest.__init__(self, ip, username, password)
        UBNTWebSocketClient.__init__(self, ip, port, username, password)

    @property
    def dimmer_level(self):
        return self.dimmer_level

    @dimmer_level.setter
    def dimmer_level(self, value):
        self._dimmer_level = value
        data = {"sensors": [{"dimmer_level": value, "port": 1}]}
        self.send_cmd(data)

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self._output = value
        data = {"sensors": [{"output": value, "port": 1}]}
        self.send_cmd(data)

    def recv_data(self, payload, isBinary):
        try:
            if not isBinary:
                data = json.loads(payload)
                if "sensors" in data and len(data['sensors']) > 0:
                    self.status = data['sensors'][0]
                    for key in self.status.keys():
                        if hasattr(self, '_' + key) and key is not 'index':
                            oldval = getattr(self, '_' + key)
                            setattr(self, '_' + key, self.status[key])
                            if oldval != self.status[key] and self.callback:
                                self.callback({self.label: {key: self.status[key], 'time': time.time() * 10}})

            else:
                pass
        except Exception as e:
            print("explody {}", e.message)
            import sys, traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('port', help="port", default=7682, nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    args = parser.parse_args()

    mFI = MSwitch(args.address, args.port, args.username, args.pwd)


    def dataReceived(data):
        print data
        # print("output is: {}, {} volts - {}".format(mFI.output,mFI.voltage,time.time()))


    mFI.callback = dataReceived

    asyncio.get_event_loop().run_forever()
