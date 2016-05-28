from socket import *
import trollius as asyncio
from MSwitch import MSwitch
from MPower import MPower

class M:
    
    idsMap = {}

    @staticmethod
    def field(id):
        def make_field(func):
            M.idsMap[id] = func
            return func
        return make_field

class MFiUdpMsgParse: 
    def __init__(self, address):
        self.device_class = None
        self.address = address

    def parse_device(self, msg):

        class ByteMe:
            index = 0
            def __init__(self, msg):
                self.msg = msg

            def next(self):
                d = self.msg[self.index]
                self.index += 1
                return int(d, base=16)

        r = ByteMe(msg)

        while r.index < len(msg):

            lsb = r.next()
            fieldId = (r.next() << 8) | lsb

            fieldLength = r.next()
            field = []

            for n in range(fieldLength):
                b = r.next()
                #conver to ascii if we can
                if b >= 36 and b < 127:
                    b = chr(b)
                field.append(b)

            self.parse_field(self, fieldId, field)

        if self.device_type == "IWD1U":
            self.device_class = MSwitch
        elif self.device_type == "IWO2U":
            self.device_class = MPower
        else:
            print("unsupported device type discovered: {}".format(self.device_type))

    def __call__(self, port=7682, user="ubnt", pwd="ubnt"):
        if not self.device_class:
            return None
        d = self.device_class(self.address, port, user, pwd)
        d.device_name = self.device_name
        d.firmware_version = self.firmware_version

        return d

    def parse_field(self, instance, id, field):
        if id in M.idsMap:
            M.idsMap[id](instance, field)

    @M.field(11)
    def parse_device_name(self, data):
        self.device_name = self._to_string(data)

    @M.field(12)
    def parse_device_type(self, data):
        self.device_type = self._to_string(data)

    @M.field(13)
    def parse_ssid(self, data):
        self.ssid = self._to_string(data)

    @M.field(3)
    def parse_firmware_version(self, data):
        self.firmware_version = self._to_string(data)        

    def _to_string(self, data):
        s = ""
        for d in data:
            s += d
        return s


class MFiDiscovery:

    def __init__(self, loop=None):
        self.devices = []

        self.discoveryPayload = bytearray()
        self.discoveryPayload.append(0x01)
        self.discoveryPayload.append(0x00)
        self.discoveryPayload.append(0x00)
        self.discoveryPayload.append(0x00)

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.sock.setblocking(0)

        self.loop = loop
        if not self.loop:
            self.loop = asyncio.get_event_loop()

        self.loop.create_task(self.sendDiscovery())
        self.loop.create_task(self.readData())

    def discover(self):
        self.sock.sendto(self.discoveryPayload, ('<broadcast>', 10001))

    @asyncio.coroutine
    def sendDiscovery(self):
        while True:
            self.discover()
            #sleep for 10 mins:
            yield asyncio.From(asyncio.sleep(600))

    @asyncio.coroutine
    def readData(self):
        while True:
            try:
                data, addrport = self.sock.recvfrom(1024)
                address, port = addrport
                self.parseData(data, address)
                
            #except BlockingIOError:
            #    yield asyncio.From(asyncio.sleep(3))

            except:
                """import sys, traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                        limit=2, file=sys.stdout)
                """
                yield asyncio.From(asyncio.sleep(3))

    def parseData(self, data, address):
        import binascii

        def split(str, num):
            return [ str[start:start+num] for start in range(0, len(str), num) ]

        msg = split(binascii.hexlify(data), 2)

        device = MFiUdpMsgParse(address)
        device.parse_device(msg)

        has = False

        for d in self.devices:
            if d.device_name == device.device_name:
                has = True
                break

        if not has:
            self.devices.append(device)

def testDiscoverMFI():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(30)
    
    payload = bytearray()
    payload.append(0x01)
    payload.append(0x00)
    payload.append(0x00)
    payload.append(0x00)

    print ("payload: {}".format(payload))
    sock.sendto(payload, ('<broadcast>', 10001))
    recv = ''
    MFIs = []
    while True:
        try:
            response = sock.recvfrom(1024)
        except:
            break
        print(response)
    # Parse response        

if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    print("discovering...")
    discovery = MFiDiscovery()
    discovery.discover()

    loop.run_until_complete(asyncio.sleep(10))

    for d in discovery.devices:
        print("discovered: {}, type: {}, address: {}".format(d.device_name, d.device_type, d.address))

    loop.run_forever()
