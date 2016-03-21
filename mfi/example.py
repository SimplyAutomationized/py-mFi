from MFiDiscovery import MFiDiscovery
from MSwitch import MSwitch

import trollius as asyncio
import parser, requests, argparse


post_url = ''


def dataReceived(data):
    global post_url
    print("1: {}".format(data))
    session = requests.Session()
    session.verify = False
    # session.post('http://{}:3000/users/1/web_requests/7/super_s3cret_mf1_string'.format(post_url), data=data)

def dataReceived2(data):
    global post_url
    print("2: {}".format(data))
    session = requests.Session()
    session.verify = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help="port", default=7682, nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    parser.add_argument('post_url', help='url to post data changes', nargs="?")
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    #
    discovery = MFiDiscovery()
    post_url = args.post_url
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(10))
    mymFI = []

    d1 = discovery.devices[0](discovery.devices[0].address, args.port, args.username, args.pwd)
    d1.callback = dataReceived
    d2 = discovery.devices[1](discovery.devices[1].address, args.port, args.username, args.pwd)
    d2.callback = dataReceived2
    
    """for device in discovery.devices:
        d = device(device.address, args.port, args.username, args.pwd)
        d.callback = dataReceived
        print("discovered: {}".format(d.device_name))
        mymFI.append(d)
    """
    asyncio.get_event_loop().run_forever()
