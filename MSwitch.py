import time
try:
    import ujson as json
except ImportError:
    import json
from mPower import *
from MFiRestClient import *
from UBNTWebSocket import *


class MSwitch(MPower, UBNTWebSocketClient, MFiRestClient):
    _dimmer_level = 0
    _output = 0
    status = {}

    def __init__(self, ip, port, username, password):
        MPower.__init__(self)
        self.label = 'Room'
        MFiRestClient.__init__(self, ip, username, password)
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
