import json
import threading
from time import sleep

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from autobahn.twisted.websocket import connectWS
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory

from mPower import *

class UBNTWebSocketClient(threading.Thread, ReconnectingClientFactory):
    def __init__(self, ip, username, password, port, useReactor=True):
        threading.Thread.__init__(self)
        self.__webSocket = WebSocketClientFactory(url="wss://{}:{}/?username={}&password={}".
                                                  format(ip, port, username, password), protocols=['mfi-protocol'])
        self.__webSocket.protocol = WebSocketClientProtocol
        self.__webSocket.protocol.onMessage = self.recv_data
        self.callback = None
        self.useReactor = useReactor
        self.start()

    def recv_data(self):
        pass

    def run(self):
        connectWS(self.__webSocket)
        if self.useReactor:
            reactor.run(installSignalHandlers=0)

    def send_cmd(self, data):
        self.__webSocket.protocol.sendMessage(json.dumps(data))

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)

    def close(self):
        reactor.stop()
        self.join()


class mSwitch(mPower, UBNTWebSocketClient):
    _dimmer_level = 0
    _output = 0

    def __init__(self, ip, username, password, port=7682, useReactor=True):
        mPower.__init__(self)
        UBNTWebSocketClient.__init__(self, ip, username, password, port, useReactor)
        self.status = {}

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
            # print payload
            self.status = json.loads(payload)['sensors'][0]
            for key in self.status.keys():
                setattr(self, '_' + key, self.status[key])
            if self.callback is not None:
                self.callback(self, self.status)
        else:
            pass


def mysend():
    val = input()
    mFI.send_cmd(val)
    reactor.callLater(10, mysend)
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('port', help="port", default=7682, nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    args = parser.parse_args()

    mFI = mSwitch(args.address, args.username, args.pwd, port=args.port)

    def callback(data):
        mFI.output = not mFI.output 
   
    mFI.callback = callback
    
    sleep(60)
    mFI.close()
