import json
import threading
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory,connectWS
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
                #{"sensors":[{"output":1,"port":1}]}
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
        #print payload



class mPower(object):

    def __init__(self):
        self.voltage = -1
        self.powerfactor = -1
        self.energy = -1
        self.current = -1
        self.power = -1
    @property
    def _power(self):
        return self.power

    @property
    def _voltage(self):
        return self.voltage

    @property
    def _powerfactor(self):
        return self.voltage

    @property
    def _energy(self):
        return self.energy

    @property
    def _current(self):
        return self.current

    @_power.setter
    def _power(self,value):
        self.power = value

    @_current.setter
    def _current(self,value):
        self.current = value

    @_voltage.setter
    def _voltage(self, value):
        self.voltage = value

    @_energy.setter
    def _energy(self,value):
        self.energy = value

    @_powerfactor.setter
    def _powerfactor(self,value):
        self.powerfactor = value


class mSwitch(mPower,mFiWebSocketClient):
    _dimmer_level = 0
    _output = 0

    def __init__(self,ip,username,password,datachangeCallback=None):
        mPower.__init__(self)
        #7682
        mFiWebSocketClient.__init__(self,"wss://{0}:9000/?username={1}&password={2}".format(ip,username,password),
                                    protocols=['mfi-protocol'])
        self.output
        self.dimmer_level
        self.callback = datachangeCallback


    @property
    def dimmer_level(self):
        return self.dimmer_level

    @dimmer_level.getter
    def dimmer_level(self):
        return self._dimmer_level

    @dimmer_level.setter
    def dimmer_level(self, value):
        self._dimmer_level = value
        data = {"sensors": [{"dimmer_level":value, "port":1}]}
        self.send_cmd(data)

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self,value):
        self._output = value
        data = {"sensors": [{"output":value,"port": 1}]}
        self.send_cmd(json.dumps(data))

    def recv_data(self, payload, isBinary):
        if not isBinary:
            print payload
            self.status = json.loads(payload)['sensors'][0]
            for key in self.status.keys():
                setattr(self, '_'+key, self.status[key])
            if self.callback is not None:
                self.callback(self.status)
        else:
            pass

def callback(data):
    print mFI.dimmer_level

if __name__ == '__main__':
    mFI = mSwitch("10.10.55.213","admin","ubnt",callback)
    connectWS(mFI)
    reactor.run()