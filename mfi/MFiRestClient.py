import requests

DIMMER = "dimmer"
SWITCH = "switch"


class MFiRestClient(object):
    """
    TODO:
        sroutes.cgi , parse into json
        log.cgi, parse into json..
        log.cgi?clr=yes, clears log

    """
    def __init__(self, ip, username, password):
        self._label = ''
        self._dimmer_mode = ''

        """Suppress urllib3"""
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        """Temporarily set device_name to ip"""
        self._device_name = ip
        self._output = 0
        self._dimmer_level = 0
        self.ip = ip
        self._lock = None
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.url = "https://{}/".format(ip)
        self.session.verify = False
        self.session.get(self.url)
        post_data = {"uri": "/", "username": self.username, "password": self.password}
        self.session.post((self.url + "/login.cgi"), headers={"Expect": ""},
                          data=post_data, allow_redirects=True)
        self.get_sensor_data()

    def get_routing_table(self):
        data = self.get('sroutes.cgi')

    def get_sensor_data(self):
        try:
            data = (self.session.get((self.url + "/mfi/sensors.cgi")))
            json_data = data.json()
            print (json_data)
            for key in json_data['sensors'][0].keys():
                setattr(self, '_' + key, json_data['sensors'][0][key])
        except:
            print("bad data returned: ", str(data))

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self.set('output', value)
        self.get_sensor_data()

    @property
    def dimmer_mode(self):
        return self._dimmer_mode

    @dimmer_mode.setter
    def dimmer_mode(self, value):
        if value is not 'switch' or value is not 'dimmer':
            raise ValueError
        self.set('dimmer_mode', value)

    @property
    def dimmer_level(self):
        self.get_sensor_data()
        return self._dimmer_level

    @dimmer_level.setter
    def dimmer_level(self, value):
        self.set('dimmer_level', value)
        self.get_sensor_data()

    @property
    def device_name(self):
        return self._device_name

    @device_name.setter
    def label(self, value):
        self.set('label', value)

    @property
    def lock(self):
        self.get_sensor_data()
        return self._lock

    @lock.setter
    def lock(self, value):
        self.set('lock', value)

    @property
    def site_survey(self):
        return self.get('survey.json.cgi')

    @property
    def signal(self):
        return self.get('signal.cgi')

    def get(self, cgi, isJSON=True):
        self.session.get('{}/{}'.format(self.url)).json()

    def set(self, resource, value):
        data = {resource: value}
        response = self.session.post(
            "{}/mfi/sensors.cgi?id={}&{}={}/".format(self.url, 1, resource, value))  # , data=data)
        return response


def mFIClientTest(mfi):
    mfi.output = 1
    mfi.dimmer_level = 0
    # mFI.dimmer_level = 50
    for x in range(1, 100, 5):
        mfi.dimmer_level = x
        time.sleep(.02)
    mfi.output = 0
    mfi.dimmer_mode = SWITCH
    time.sleep(5)
    mfi.lock=1

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    args = parser.parse_args()
    mFI = MFiRestClient(args.address, args.username, args.pwd)
