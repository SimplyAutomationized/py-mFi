

class mPower(object):

    def __init__(self):
        self.voltage = -1
        self.powerfactor = -1
        self.energy = -1
        self.current = -1
        self.power = -1
    @property
    def _power(self):
        return self.power

    @property
    def _voltage(self):
        return self.voltage

    @property
    def _powerfactor(self):
        return self.voltage

    @property
    def _energy(self):
        return self.energy

    @property
    def _current(self):
        return self.current

    @_power.setter
    def _power(self,value):
        self.power = value

    @_current.setter
    def _current(self,value):
        self.current = value

    @_voltage.setter
    def _voltage(self, value):
        self.voltage = value

    @_energy.setter
    def _energy(self,value):
        self.energy = value

    @_powerfactor.setter
    def _powerfactor(self,value):
        self.powerfactor = value