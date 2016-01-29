import requests

DIMMER = "dimmer"
SWITCH = "switch"

class MFiRestClient:
    """
    TODO:
        sroutes.cgi , parse into json
        log.cgi, parse into json..
        log.cgi?clr=yes, clears log

    """
    def __init__(self, ip, username, password):
        self._label = ''
        self._dimmer_mode = ''

        """Temporarily set device_name to ip"""
        self.device_name = ip
        
        self.ip = ip
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

    def get_sensor_data(self):
        data = (self.session.get((self.url + "/mfi/sensors.cgi")))
        json_data = data.json()
        for key in json_data['sensors'][0].keys():
            setattr(self, '_' + key, json_data['sensors'][0][key])

    @property
    def dimmer_mode(self):
        return self._dimmer_mode

    @dimmer_mode.setter
    def dimmer_mode(self, value):
        if value is not 'switch' or value is not 'dimmer':
            raise ValueError
            self.set('dimmer_mode', value)
            self.get_sensor_data()

            # def label(self):
            #     return self._label
            #
            # @label.setter
            # def label(self, value):
            #     '''
            #     TODO: set label using rest post
            #     :param value:
            #     :return:
            #     '''
            #     #self._label = value
            #
            #
            #
            # def send_cfgcmd(self, config_string):
            #     files = {'file': ('config.cfg', config_string)}
            #     p = self.session.post((self.url + "/system.cgi"), files=files)
            #     return p.text

    def site_survey(self):
        return self.get('survey.json.cgi')

    def signal(self):
        return self.get('signal.cgi')

    def get(self, cgi, isJSON=True):
        self.session.get('{}/{}'.format(self.url)).json()

    def set(self, resource, value):
        data = {resource: value}
        response = self.session.put("{}/sensors/1/".format(self.url), data=data)
        return response


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="address", default="localhost", nargs="?")
    parser.add_argument('username', help='username', default='ubnt', nargs="?")
    parser.add_argument('pwd', help='password', default='ubnt', nargs="?")
    args = parser.parse_args()
    mFI = MFiRestClient(args.address, args.username, args.pwd)
    print mFI.dimmer_mode
    mFI.dimmer_mode = SWITCH
    print mFI.dimmer_mode
