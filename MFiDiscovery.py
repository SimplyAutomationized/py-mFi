from socket import *
import trollius as asyncio

class MFiDiscover:

    class Protocol(asyncio.Protocol):
        transport = None
    
        def connection_made(self, transport):
            self.transport = transport
            print("connection made")


        def data_received(self, data):
            print("Received:", data)

            self.transport.close()

        def connection_lost(self, exc):
            # The socket has been closed, stop the event loop
            loop.stop()

    def __init__(self, loop=None):
        self.discoveryPayload = bytearray()
        self.discoveryPayload.append(0x01)
        self.discoveryPayload.append(0x00)
        self.discoveryPayload.append(0x00)
        self.discoveryPayload.append(0x00)

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        #sock.settimeout(3)

        self.loop = loop
        if not self.loop:
            self.loop = asyncio.get_event_loop()

        connect_coro = self.loop.create_connection(MFiDiscover.Protocol, sock=self.sock)
        self.transport, self.protocol = self.loop.run_until_complete(connect_coro)      

        self.protocol.data_received = self._data_received

        self.loop.create_task(self.sendDiscovery())

    @asyncio.coroutine
    def sendDiscovery(self):
        while True:
            print("sending discovery packet")
            self.sock.sendto(self.discoveryPayload, ('<broadcast>', 10001))
            #sleep for 10 mins:
            yield asyncio.From(asyncio.sleep(600))

    def _data_received(self, data):
        print("Received:", data)

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