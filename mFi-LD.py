import json
from threading import Thread
from time import sleep
import ssl

from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

from mPower import *

import trollius as asyncio

class UbntWebSocketProtocol(WebSocketClientProtocol):

    def onOpen(self):
        self.factory.client.sendMessage = self.sendMessage

class UBNTWebSocketClient():
    def __init__(self, ip, port, username, password, loop=None):
        self.__webSocket = WebSocketClientFactory(url="wss://{}:{}/?username={}&password={}".
                                                  format(ip, port, username, password), protocols=['mfi-protocol'])
        self.addy = ip
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
                yield asyncio.From(self.loop.create_connection(self.__webSocket, self.addy, self.port, ssl=ssl.SSLContext(ssl.PROTOCOL_SSLv23)))          
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

    def recv_data(self):
        pass

    def send_cmd(self, data):
        self.sendMessage(json.dumps(data))

    def sendMessage(self, data):
        pass

    def clientConnectionFailed(self, wasClean, code, reason):
        print("Client connection failed .. retrying ..")
        self.loop.create_task(self._connect())

class mSwitch(mPower, UBNTWebSocketClient):
    _dimmer_level = 0
    _output = 0
    status = {}
    def __init__(self, ip, port, username, password):
        mPower.__init__(self)
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
                    status = data['sensors'][0]
                    for key in status.keys():
                        setattr(self, '_' + key, status[key])
                        if self.callback:
                            self.callback(status)
            else:
                pass
        except:
            print("explody")
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

    mFI = mSwitch(args.address, args.port, args.username, args.pwd)

    def dataReceived(data):
        print("switch is: {}".format(mFI.output))
   
    mFI.callback = dataReceived
    
    asyncio.get_event_loop().run_forever()

    
