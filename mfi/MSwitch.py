import time
try:
    import ujson as json
except ImportError:
    import json
from MPower import MPower



class MSwitch(MPower):
    _dimmer_level = 0
    _output = 0
    _lock = 0
    status = {}
    callback=None

    def __init__(self, ip, port, username, password):
        MPower.__init__(self, ip, port, username, password)

    @property
    def dimmer_level(self):
        return self.dimmer_level

    @dimmer_level.setter
    def dimmer_level(self, value):
        self._dimmer_level = value
        data = {"sensors": [{"dimmer_level": value, "port": 1}]}
        self.send_cmd(data)


if __name__ == '__main__':
    import argparse
    import trollius as asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('port', help="port", default=7682, nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    args = parser.parse_args()

    mFI = MSwitch(args.address, args.port, args.username, args.pwd)

    def dataReceived(data):
        print(data)
        # print("output is: {}, {} volts - {}".format(mFI.output,mFI.voltage,time.time()))


    mFI.callback = dataReceived

    asyncio.get_event_loop().run_forever()
