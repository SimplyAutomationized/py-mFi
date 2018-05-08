#!/usr/bin/env python

from .UBNTWebSocket import UBNTWebSocketClient
from pysignals import Signal


try:
    import ujson as json
except ImportError:
    import json


class Output(object):
    def __init__(self, index, parent):
        self.index = index
        self._output = None
        self.parent = parent
        self.output_changed = Signal(providing_args=["value"])
        self.power_changed = Signal(providing_args=["value"])

        self._voltage = -1
        self._powerfactor = -1
        self._energy = -1
        self._current = -1
        self._power = -1
        
        #need a _ready property to indicate that the output exists and has a known state
        self._ready = False

    @property
    def ready(self):
        return self._ready

    @property
    def power(self):
            return self._power

    @property
    def voltage(self):
            return self._voltage

    @property
    def powerfactor(self):
            return self._powerfactor

    @property
    def energy(self):
            return self._energy

    @property
    def current(self):
            return self._current

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self.parent.set_output(self.index, value)

    def update(self, status):
        def check_signal(key, value):
            changed_sig = key + '_changed'

            if hasattr(self, changed_sig):
                signal = getattr(self, changed_sig)
                signal.send(sender=self, value=value)

        for key in status.keys():
            if "output" in status.keys():
                self._ready = True
            if hasattr(self, '_' + key) and key is not 'index':
                oldval = getattr(self, '_' + key)
                if status[key] != oldval:
                    setattr(self, '_' + key, status[key])
                    check_signal(key, status[key])

class MPower(UBNTWebSocketClient):
    _lock = -1

    def __init__(self, ip, port=7682, username="ubnt", password="ubnt", device_name = "unknown"):

        #MFiRestClient.__init__(self, ip, username, password)
        UBNTWebSocketClient.__init__(self, ip, port, username, password)

        self.device_name = device_name
        self.num_outputs_changed = Signal(providing_args=["num_outputs"])
        self.outputs = []
        self.OutputClass = Output

    def output(self, port):
        for out in self.outputs:
            if out.index == port:
                return out

    def set_output(self, port, value):
        data = {"sensors": [{"output": value, "port": port}]}
        self.send_cmd(data)

    def recv_data(self, payload):

        payloads = payload.split("}{")

        for p in payloads:
            if not p.endswith("}"):
                p += "}"
            if not p.startswith("{"):
                p = "{" + p

            try:
                data = json.loads(p)

                if "sensors" in data and len(data['sensors']) > 0:
                    status = data['sensors'][0]

                    index = status['port']
                    found = False

                    for o in self.outputs:
                        if o.index == index:
                            found = True
                            o.update(status)

                    if not found:
                        new_output = self.OutputClass(index, self)
                        self.outputs.append(new_output)
                        self.num_outputs_changed.send(sender=self.__class__, num_outputs=len(self.outputs))

            except Exception as e:
                print("device address: {}".format(self.ip))
                print("explody {}".format(e.message))
                print("msg: {}".format(p))

                import sys, traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=6, file=sys.stdout)

if __name__ == '__main__':
    import argparse

    if sys.version_info >= (3,0):
        import asyncio
    else:
        import trollius as asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('port', help="port", default=7682, nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    parser.add_argument('--on', help='toggle output', action="store_true")
    parser.add_argument('--off', help='toggle output off', action="store_true")
    parser.add_argument('--output', help='output index', type=int, default=1)
    parser.add_argument('--num_outputs', help='number of outlets', type=int, default=8)


    args = parser.parse_args()

    mFI = MPower(args.address, args.port, args.username, args.pwd)

    outputs = []

    def output_changed(signal, sender, value):
        print("output {} changed to {}".format(sender.index, value))

    def outputs_changed(signal, sender, num_outputs):
        print("number of outputs: {}".format(num_outputs))

        for o in mFI.outputs:
            if not o in outputs:
                outputs.append(o)
                o.output_changed.connect(output_changed)

    mFI.num_outputs_changed.connect(outputs_changed)

    asyncio.coroutine
    def do_command():
        
        while len(outputs) < args.num_outputs:
             yield asyncio.From(asyncio.sleep(1.0))
      
        output = mFI.output(args.output)
       
        if not output:
            print ("output {} does not exist".format(args.output))
            return
        
        while not output.ready:
            yield asyncio.From(asyncio.sleep(1.0))

        if args.on:
            output.output = True
            while not output.output:
                yield asyncio.From(asyncio.sleep(0.5))

        elif args.off:
            output.output = False
            while output.output == True:
                yield asyncio.From(asyncio.sleep(0.5))
                
        else:
            while True:
                yield asyncio.From(asyncio.sleep(0.5))
    
        

    asyncio.get_event_loop().run_until_complete(do_command())
