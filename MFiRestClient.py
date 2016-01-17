import requests


class MFiRestClient:
    def __init__(self, ip, username, password):
        self._label = ''
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
        data = (self.session.get((self.url + "/mfi/sensors.cgi"))).json()
        for key in data['sensors'][0].keys():
            setattr(self, key, data['sensors'][0][key])

            # @property
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
