from socket import *
import trollius as asyncio

class MFiDiscover:

    class Protocol(asyncio.Protocol):
        transport = None
    
        def connection_made(self, transport):
            self.transport = transport
            print("connection made")


        def data_received(self, data):
            print("Received:", data.decode())

            self.transport.close()

        def connection_lost(self, exc):
            # The socket has been closed, stop the event loop
            loop.stop()

    def __init__(self, loop=None):
        self.discoveryPacket = 0x01000000
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.sock.sendto(bytearray.fromhex(str(self.discoveryPacket)), ('<broadcast>', 10001))
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
            
            #sleep for 10 mins:
            yield asyncio.From(asyncio.sleep(600))

    def _data_received(self, data):
        print("Received:", data.decode())

def testDiscoverMFI():
    data = 0x01000000
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(30)
    sock.sendto(bytearray.fromhex(str(data)), ('<broadcast>', 10001))
    recv = ''
    MFIs = []
    while True:
        try:
            response = sock.recvfrom(1024)
        except:
            break
        print response
    # Parse response        

if __name__ == '__main__':

    testDiscoverMFI()

    #discovery = MFiDiscover()

    #asyncio.get_event_loop().run_forever()