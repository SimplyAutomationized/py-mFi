from socket import *
from time import sleep


def discoverMFI():
    data = 0x01000000
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(3)
    sock.sendto(bytearray.fromhex(data), ('<broadcast>', 10001))
    recv = ''
    MFIs = []
    while True:
        try:
            response = sock.recvfrom(1024)
        except socket.timeout:
            break
    print response
    # Parse response
