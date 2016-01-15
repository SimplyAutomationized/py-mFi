class mPower(object):
    def __init__(self):
        self._voltage = -1
        self._powerfactor = -1
        self._energy = -1
        self._current = -1
        self._power = -1

    @property
    def power(self):
        return self._power

    @property
    def voltage(self):
        return self._voltage

    @property
    def powerfactor(self):
        return self._powerfactor

    @property
    def energy(self):
        return self._energy

    @property
    def current(self):
        return self._current

    @power.setter
    def power(self, value):
        self._power = value

    @current.setter
    def current(self, value):
        self._current = value

    @voltage.setter
    def voltage(self, value):
        self._voltage = value

    @energy.setter
    def energy(self, value):
        self._energy = value

    @powerfactor.setter
    def powerfactor(self, value):
        self._powerfactor = value
