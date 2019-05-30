"""
Author: Romain Fafet (farom57@gmail.com)
"""

import time

import PyIndi


class IndiClient(PyIndi.BaseClient):
    def __init__(self, st):
        super(IndiClient, self).__init__()
        self.st = st
        self.telescope_name = None
        self.telescope = None
        self.telescope_prop = {
            "CONNECTION": None,
            "EQUATORIAL_EOD_COORD": None,
            "ON_COORD_SET": None,
            "TELESCOPE_MOTION_dec": None,
            "TELESCOPE_MOTION_WE": None,
            "TELESCOPE_TIMED_GUIDE_dec": None,
            "TELESCOPE_TIMED_GUIDE_WE": None,
            "TELESCOPE_CURRENT_RATE": None,
            "TELESCOPE_SLEW_RATE": None,
            "TELESCOPE_PIER_SIDE": None}
        self.telescope_features = {
            "minimal": False,
            "move": False,
            "timed": False,
            "speed": False,
            "pier": False,
            "rate": False}
        self.joystick = None
        self.joystick_axes = None

    def newDevice(self, d):
        self.st.log(2, "New device: " + d.getDeviceName())

        if d.getDeviceName() == "Joystick":
            self.joystick = d
        else:
            self.st.ui.add_telescope(d.getDeviceName())

    def newProperty(self, p):
        if p.getDeviceName() == self.telescope_name:
            if p.getName() in self.telescope_prop.keys():
                self.telescope_prop[p.getName()] = p
                self.update_telescope_features()

        if p.getDeviceName() == "Joystick":
            if p.getName() == "CONNECTION":
                # try to connect
                p.getSwitch()[0].s = PyIndi.ISS_ON
                p.getSwitch()[1].s = PyIndi.ISS_OFF
                self.sendNewSwitch(p.getSwitch())
            elif p.getName() == "JOYSTICK_AXES":
                self.joystick_axes = p.getNumber()
                self.st.ui.add_joystick()

    def removeProperty(self, p):
        if p.getDeviceName() == self.telescope_name:
            if p.getName() in self.telescope_prop.keys():
                self.telescope_prop[p.getName()] = None
                self.update_telescope_features()

    def newBLOB(self, bp):
        pass

    def newSwitch(self, svp):
        pass

    def newNumber(self, nvp):
        if nvp.device == self.telescope_name and nvp.name == "EQUATORIAL_EOD_COORD":
            self.st.update_tracking(nvp[0].value, nvp[1].value)
        if nvp.device == "Joystick" and nvp.name == "JOYSTICK_AXES":
            self.st.update_joystick_offset(nvp)

    def newText(self, tvp):
        pass

    def newLight(self, lvp):
        pass

    def newMessage(self, d, m):
        pass

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        if self.st.ui is not None:
            self.st.ui.disconnected()

    def set_telescope(self, device_name):
        """Configure the device as telescope (try to connect & check properties). Return True if successful"""
        self.telescope_name = device_name
        self.telescope = None
        self.telescope_prop = {
            "CONNECTION": None,
            "EQUATORIAL_EOD_COORD": None,
            "ON_COORD_SET": None,
            "TELESCOPE_MOTION_dec": None,
            "TELESCOPE_MOTION_WE": None,
            "TELESCOPE_TIMED_GUIDE_dec": None,
            "TELESCOPE_TIMED_GUIDE_WE": None,
            "TELESCOPE_CURRENT_RATE": None,
            "TELESCOPE_SLEW_RATE": None,
            "TELESCOPE_PIER_SIDE": None}
        self.telescope_features = {
            "minimal": False,
            "move": False,
            "timed": False,
            "speed": False,
            "pier": False,
            "rate": False}

        self.telescope = self.getDevice(device_name)
        if self.telescope is None:
            self.st.log(0, "Error during driver connection: Driver not found: " + device_name)
            return False

        self.watchDevice(self.telescope_name)

        # Check existing properties (new ones will be detected later by newProperty())
        for key in self.telescope_prop:
            prop = self.telescope.getProperty(key)
            if prop:
                self.telescope_prop[key] = prop

        t = 0
        while self.telescope_prop["CONNECTION"] is None:
            if t > self.st.connection_timeout:
                self.st.log(0, "Error during driver connection: CONNECT property not found")
                return False
            time.sleep(0.05)
            t = t + 0.05

        if not (self.telescope.isConnected()):
            self.telescope_prop["CONNECTION"].getSwitch()[0].s = PyIndi.ISS_ON
            self.telescope_prop["CONNECTION"].getSwitch()[1].s = PyIndi.ISS_OFF
            self.sendNewSwitch(self.telescope_prop["CONNECTION"].getSwitch())

        self.update_telescope_features()

        # Required set of properties:
        # - Minimal: CONNECT, EQUATORIAL_EOD_COORD, ON_COORD_SET
        # - Move: TELESCOPE_MOTION_dec, TELESCOPE_MOTION_WE
        # - Timed move: TELESCOPE_TIMED_GUIDE_dec, TELESCOPE_TIMED_GUIDE_WE
        # - Speed: TELESCOPE_CURRENT_RATE
        # - Other: TELESCOPE_SLEW_RATE, TELESCOPE_PIER_SIDE

        t = 0
        while not (self.telescope_features["minimal"] &
                   (self.telescope_features["move"] or
                    self.telescope_features["timed"] or
                    self.telescope_features["speed"])):
            if t > self.st.connection_timeout:
                self.st.log(0,
                            "Error during driver connection: No control method available, Is \"" + device_name +
                            "\" a telescope device ?")
                return False
            time.sleep(0.05)
            t = t + 0.05

        self.update_telescope_features()
        self.st.log(2, device_name + " connected")
        return True

    def update_telescope_features(self):
        telescope_requirements = {
            "minimal": {"CONNECTION", "EQUATORIAL_EOD_COORD", "ON_COORD_SET"},
            "move": {"TELESCOPE_MOTION_dec", "TELESCOPE_MOTION_WE"},
            "timed": {"TELESCOPE_TIMED_GUIDE_dec", "TELESCOPE_TIMED_GUIDE_WE"},
            "speed": {"TELESCOPE_CURRENT_RATE"},
            "pier": {"TELESCOPE_PIER_SIDE"},
            "rate": {"TELESCOPE_SLEW_RATE"}}
        old = self.telescope_features

        for feat in telescope_requirements:
            satisfied = True
            for req in telescope_requirements[feat]:
                if self.telescope_prop[req] is None:
                    satisfied = False
            self.telescope_features[feat] = satisfied

        if not (old == self.telescope_features) & (self.st.ui is not None):
            self.st.ui.update_telescope_features(self.telescope_features)

    def set_speed(self, ra_speed: float, dec_speed: float):
        """ send the command to change the speed of the telescope (in deg/s) """

        if not self.telescope_features["speed"]:
            raise Error("Variable motion rate not supported by {0}".format(self.telescope_name))

        rate_prop = self.telescope.getNumber("TELESCOPE_CURRENT_RATE")

        ra_speed = ra_speed / 360 * 86164.1
        dec_speed = dec_speed / 360 * 86164.1
        if ra_speed > rate_prop[0].max:
            ra_speed = rate_prop[0].max
        if dec_speed > rate_prop[1].max:
            dec_speed = rate_prop[1].max
        if ra_speed < rate_prop[0].min:
            ra_speed = rate_prop[0].min
        if dec_speed < rate_prop[1].min:
            dec_speed = rate_prop[1].min

        rate_prop[0].value = ra_speed
        rate_prop[1].value = dec_speed
        self.sendNewNumber(rate_prop)


class Error(Exception):
    pass
