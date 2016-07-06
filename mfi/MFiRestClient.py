import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

DIMMER = "dimmer"
SWITCH = "switch"

class RestOutput():

    def __init__(self, index, parent):

        self.index = index
        self.parent = parent
        self._device_name = None
        self._output = 0
        self._dimmer_level = 0
        self._thismonth = 0
        self._prevmonth = 0
        self._lock = None
        self._label = ''
        self._dimmer_mode = ''  
        self._power = None
        
    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self.parent.set(self.index, "output", value)

    @property
    def power(self):
        return self._power

    @property
    def dimmer_mode(self):
        return self._dimmer_mode

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
        self.parent.set('lock', value)

    @property
    def thismonth(self):
        return self._thismonth * 1/3200

    @property
    def prevmonth(self):
        return self._prevmonth * 1/3200

    @property
    def site_survey(self):
        return self.parent.get('survey.json.cgi')

    @property
    def signal(self):
        return self.parent.get('signal.cgi')

    @property
    def port(self):
        return self.index

    def update(self, status):
        for key in status.keys():
            setattr(self, '_' + key, status[key])


class MFiRestClient(object):
    """
    TODO:
        sroutes.cgi , parse into json
        log.cgi, parse into json..
        log.cgi?clr=yes, clears log

    """
    def __init__(self, ip, username, password):
        self.outputs = []

        """Suppress urllib3"""
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        """Temporarily set device_name to ip"""
       
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

    def get_sensor_data(self, debug=False):
        try:
            data = (self.session.get((self.url + "/mfi/sensors.cgi")))
            json_data = data.json()
            
            sensors = json_data['sensors']
            if debug:
                print("sensors = {}".format(sensors))

            for output in sensors:
                _output = None
                
                for o in self.outputs:
                    if o.port == output["port"]:
                        
                        _output = o

                if not _output:
                    _output = RestOutput(output["port"], self)
                    self.outputs.append(_output)

                _output.update(output)

        except:
            import sys, traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=6, file=sys.stdout)

    def get(self, cgi, isJSON=True):
        self.session.get('{}/{}'.format(self.url)).json()

    def set(self, sensor_id, key, value):
        data = {resource: value}
        response = self.session.post(
            "{}/mfi/sensors.cgi?id={}&{}={}/".format(self.url, sensor_id, key, value))  # , data=data)
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

    mFi = MFiRestClient(args.address, args.username, args.pwd)
    mFi.get_sensor_data(debug=True)
