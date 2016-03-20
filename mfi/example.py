from MFiDiscovery import MFiDiscovery
from MSwitch import MSwitch

import trollius as asyncio
import parser, requests, argparse


post_url = ''


def dataReceived(data):
    global post_url
    print data
    session = requests.Session()
    session.verify = False
    # session.post('http://{}:3000/users/1/web_requests/7/super_s3cret_mf1_string'.format(post_url), data=data)


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

    for device in discovery.devices:
        d = device.device_class(device.address, args.port, args.username, args.pwd)
        d.device_name = device.device_name
        d.callback = dataReceived
        mymFI.append(d)

    asyncio.get_event_loop().run_forever()
