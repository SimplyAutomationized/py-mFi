import time
try:
    import ujson as json
except ImportError:
    import json
from MPower import MPower, Output

from pysignals import Signal


class DimmerOutput(Output):

    def __init__(self, index, parent):
        Output.__init__(self, index, parent)
        _dimmer_level = 0
        _lock = 0

        self.dimmer_level_changed = Signal(providing_args=["value"])


    @property
    def dimmer_level(self):
        return self.dimmer_level

    @dimmer_level.setter
    def dimmer_level(self, value):
        data = {"sensors": [{"dimmer_level": value, "port": 1}]}
        self.parent.send_cmd(data)


class MSwitch(MPower):

    def __init__(self, ip, port, username, password):
        MPower.__init__(self, ip, port, username, password)
        self.OutputClass = DimmerOutput

    @property
    def dimmer_level(self):
        if not len(self.outputs):
            print("no outputs on device.  not connected?")
            return None

        return self.outputs[0].dimmer_level

    @dimmer_level.setter
    def dimmer_level(self, value):
        if not len(self.outputs):
            print("no outputs on device.  not connected?")
            return None

        self.outputs[0].dimmer_level = value


if __name__ == '__main__':
    import argparse
    import trollius as asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('port', help="port", default=7682, nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    parser.add_argument('--dim', help='dim level', type=int, default=None)

    args = parser.parse_args()

    mFI = MSwitch(args.address, args.port, args.username, args.pwd)

    def dim(level):
        try:
            mFI.set_output(1, True)
            mFI.dimmer_level = level
        except:
            import sys, traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=6, file=sys.stdout)

    if args.dim:
        asyncio.get_event_loop().call_later(5, dim, args.dim)

    asyncio.get_event_loop().run_forever()
