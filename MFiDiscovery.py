from socket import *
import trollius as asyncio

class MFiDiscover:

    def __init__(self, loop=None):
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

    @asyncio.coroutine
    def sendDiscovery(self):
        while True:
            print("sending discovery packet")
            self.sock.sendto(self.discoveryPayload, ('<broadcast>', 10001))
            #sleep for 10 mins:
            yield asyncio.From(asyncio.sleep(600))

    @asyncio.coroutine
    def readData(self):
        while True:
            try:
                data, addrport = self.sock.recvfrom(1024)
                address, port = addrport
                self.parseData(data, address)
                
            except BlockingIOError:
                yield asyncio.From(asyncio.sleep(3))
            except:
                import sys, traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                        limit=2, file=sys.stdout)
                yield asyncio.From(asyncio.sleep(3))

    def parseData(self, data, address):
        import binascii

        def split(str, num):
            return [ str[start:start+num] for start in range(0, len(str), num) ]

        msg = split(binascii.hexlify(data), 2)

        print("msg length: {}".format(len(msg)))
        i=0
        print("byte\t : hex\t : ascii\t : dec")
        for b in msg:
            c = ''
            if int(b, base=16) >= 36 and int(b, base=16) < 127:
                c = chr(data[i])
            print("{}\t : {}\t : {}\t : {}".format(i, b, c, int(b, base=16)))
            i+=1

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

            print("field id: {}".format(fieldId))

            fieldLength = r.next()

            print("field length: {}".format(fieldLength))

            field = []
            for n in range(fieldLength):
                b = r.next()
                #conver to ascii if we can
                if b >= 36 and b < 127:
                    b = chr(b)
                field.append(b)

            print("field:", field)

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

    #testDiscoverMFI()

    discovery = MFiDiscover()

    asyncio.get_event_loop().run_forever()