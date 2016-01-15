import json
from mPower import *
import threading
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
from time import sleep
from twisted.internet import reactor

from twisted.internet.protocol import ReconnectingClientFactory

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

mFI = None


class mFiWebSocketClient(WebSocketClientFactory, ReconnectingClientFactory):
    class mFiWebSocketClientProtocol(WebSocketClientProtocol):
        def onOpen(self):
            self.sendMessage('{"time":10}')
            self.factory.send_cmd = self.send_cmd

        def onMessage(self, payload, isBinary):
            self.factory.recv_data(payload, isBinary)

        def send_cmd(self, data):
            print data
            # {"sensors":[{"output":1,"port":1}]}
            self.sendMessage(json.dumps(data))

    protocol = mFiWebSocketClientProtocol
    status = {}

    def send_cmd(self, payload, isBinary=False):
        pass

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)

    def recv_data(self, payload, isBinary):
        self.status = json.loads(payload)['sensors'][0]


class mSwitch(mPower, mFiWebSocketClient):
    _dimmer_level = 0
    _output = 0

    def __init__(self, ip, username, password, port=7682):
        mPower.__init__(self)
        mFiWebSocketClient.__init__(self, "wss://{}:{}/?username={}&password={}".format(ip, port, username, password),
                                    protocols=['mfi-protocol'])
        # self.output
        # self.dimmer_level
        self.callback = None

    @property
    def dimmer_level(self):
        return self.dimmer_level

    @dimmer_level.getter
    def dimmer_level(self):
        return self._dimmer_level

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
        if not isBinary:
            #print payload
            self.status = json.loads(payload)['sensors'][0]
            for key in self.status.keys():
                setattr(self, '_' + key, self.status[key])
            if self.callback is not None:
                self.callback(self.status)
        else:
            pass


def callback(data):
    mFI.output = not mFI.output




if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('port', help="port", default=7682, nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    args = parser.parse_args()

    mFI = mSwitch(args.address, args.username, args.pwd, port=args.port)
    mFI.callback = callback
    connectWS(mFI)
    reactor.run()
