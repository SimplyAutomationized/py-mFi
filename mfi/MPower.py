#!/usr/bin/env python

from .UBNTWebSocket import UBNTWebSocketClient
from PySignal import ClassSignal

try:
    import ujson as json
except ImportError:
    import json


class Output(object):
    def __init__(self, index, parent):
        self.index = index
        self._output = None
        self.parent = parent
        self.output_changed = ClassSignal()
        self.power_changed = ClassSignal()

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
                signal.emit(value)

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
        self.num_outputs_changed = ClassSignal()
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
                        self.num_outputs_changed.emit(self.outputs)

            except Exception as e:
                print("device address: {}".format(self.ip))
                print("explody {}".format(e.message))
                print("msg: {}".format(p))

                import sys, traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=6, file=sys.stdout)
