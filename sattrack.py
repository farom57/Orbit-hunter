"""
Author: Romain Fafet (farom57@gmail.com)
"""
from skyfield.api import load, Topos, Star, EarthSatellite
from skyfield.units import Angle
import PyIndi
import time


class SatTrack(object):
    """ SatTrack is the core class of pysattrack

    The configuration is performed by the GUI by changing the attributs.
    INDI connection is controled by connect() and disconnect() and the tracking
    by start(), stop(), move(ra_angle,dec_angle) and goto_rise_and_wait().
    """

    def __init__(self):

        # configuration variables: they that can be assessed by the UI and saved
        self.indi_server_ip = "127.0.0.1"
        self.indi_port = 7624
        self.indi_telescope_driver = ""
        self.indi_joystick_driver = ""

        self.catalogs = [
            CatalogItem("Recent launches", "https://celestrak.com/NORAD/elements/tle-new.txt", True),
            CatalogItem("Space stations", "https://celestrak.com/NORAD/elements/stations.txt", True),
            CatalogItem("100 brightest", "https://celestrak.com/NORAD/elements/visual.txt", True),
            CatalogItem("Active satellites", "https://celestrak.com/NORAD/elements/active.txt", False),
            CatalogItem("Geosynchronous", "https://celestrak.com/NORAD/elements/geo.txt", False),
            CatalogItem("Iridium", "https://celestrak.com/NORAD/elements/iridium.txt", False),
            CatalogItem("Iridium NEXT", "https://celestrak.com/NORAD/elements/iridium-NEXT.txt", False),
            CatalogItem("Globalstar", "https://celestrak.com/NORAD/elements/globalstar.txt", False),
            CatalogItem("Intelsat", "https://celestrak.com/NORAD/elements/intelsat.txt", False),
            CatalogItem("SES", "https://celestrak.com/NORAD/elements/ses.txt", False),
            CatalogItem("Orbcomm", "https://celestrak.com/NORAD/elements/orbcomm.txt", False),
            CatalogItem("Amateur Radio", "https://celestrak.com/NORAD/elements/amateur.txt", False)
        ]
        self._selected_satellite = 'ISS (ZARYA)'

        self._observer_alt = 5
        self._observer_lat = "43.538 N"
        self._observer_lon = "6.955 E"
        self.observer_offset = 0  # in days

        self.track_method = 0  # 0 = GOTO, 1 = Move, 2 = Timed moves, 3 = Speed

        self.p_gain = 0.5
        self.tau_i = 3
        self.tau_d = 1
        self.max_rate = 1  # deg/s
        self.i_sat = 0.5

        self.connection_timeout = 1

        # dynamic data
        self.ui = None
        self.indiclient = IndiClient(self)
        self.ts = load.timescale()
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)
        self.update_tle()
        self.tracking = False

        self.sat = self.satellites_tle[self._selected_satellite]  # TODO: add error management

    # Some properties to maintain to preserve internal consistency when attributes are updated and for error management
    @property
    def selected_satellite(self):
        return self._selected_satellite

    @selected_satellite.setter
    def selected_satellite(self, n_sat):
        # ensure that the satellite name is correct, manage the case of satellites whose key (name) is a number
        try:
            self.sat = self.satellites_tle[n_sat]
        except:
            try:
                self.sat = self.satellites_tle[int(n_sat)]
            except:
                pass
            else:
                self._selected_satellite = int(n_sat)
        else:
            self._selected_satellite = n_sat

    def set_tle(self, tle):
        lines = tle.strip().splitlines()
        self.sat = EarthSatellite(lines[0], lines[1])
        self._selected_satellite = "TLE"

    @property
    def observer_alt(self):
        return self._observer_alt

    @observer_alt.setter
    def observer_alt(self, n_alt):
        # A valueError will be raised by Topos in cas of incorrect arguments. In this case the error is transfered to
        # the upper level without modifying_the property
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, n_alt)
        self._observer_alt = n_alt

    @property
    def observer_lat(self):
        return self._observer_lat

    @observer_lat.setter
    def observer_lat(self, n_lat):
        # A valueError will be raised by Topos in cas of incorrect arguments. In this case the error is transfered to
        # the upper level without modifying_the property
        self.obs = Topos(n_lat, self._observer_lon, None, None, self._observer_alt)
        self._observer_lat = n_lat

    @property
    def observer_lon(self):
        return self._observer_lon

    @observer_lon.setter
    def observer_lon(self, n_lon):
        # A valueError will be raised by Topos in cas of incorrect arguments. In this case the error is transfered to
        # the upper level without modifying_the property
        self.obs = Topos(self._observer_lat, n_lon, None, None, self._observer_alt)
        self._observer_lon = n_lon

    # Utility functions
    def sat_pos(self, t=None):
        """ Satellite position: ra, dec, distance"""
        diff = self.sat - self.obs
        if t is None:
            t = self.t()
        topocentric = diff.at(t)
        ra, dec, distance = topocentric.radec()
        return ra, dec, distance

    def telescope_pos(self):
        """ Telescope position: ra, dec """
        if self.indiclient.telescope_features["minimal"]:
            radec = self.indiclient.telescope.getNumber("EQUATORIAL_EOD_COORD")
            star = Star(ra_hours=radec[0].value, dec_degrees=radec[1].value)
            # alt, az = self.obs.at(self.t()).observe(star).apparent().altaz()
            return star.ra, star.dec
        else:
            raise Error("Unable to get the coordinates from the telescope")

    def radec2altaz(self, ra: Angle, dec: Angle):
        # TODO: simplified version of skyfield "_to_altaz" function
        return 0, 0

    def t(self):
        """ Current software time"""
        tmp = self.ts.now().tt + self.observer_offset
        return self.ts.tt(jd=tmp)

    def set_time(self, year, month=1, day=1, hour=0, minute=0, second=0.0):
        self.observer_offset = self.ts.utc(year, month, day, hour, minute, second).tt - self.ts.now().tt

    def t_iso(self):
        """ Current software time in iso format"""
        tmp = self.ts.now().tt + self.observer_offset
        return self.ts.tt(jd=tmp).utc_iso()

    def log(self, level, text):
        """ level: 0 for error, 1 for warning, 2 for common messages, 3 for extended logging """
        print(text)
        # TODO add logs into ui

    def update_tle(self, max_age=0):
        """ Update satellite elements, only elements older than 'max_age' days are downloaded  """
        self.satellites_tle = dict()
        for catalog in self.catalogs:
            if catalog.active:
                current_tle = load.tle(catalog.url)  # TODO: add error management
                age = self.t() - current_tle[list(current_tle)[0]].epoch
                self.log(2, 'TLE for ' + catalog.name + ' are {:.3f} days old'.format(age))
                if abs(age) > max_age:
                    self.log(1, 'Updating TLE'.format(age))
                    current_tle = load.tle(catalog.url, reload=True)
                self.satellites_tle.update(current_tle)

        if self.ui is not None:
            self.ui.update_sat_list()

    # INDI connection
    def connect(self):
        if self.is_connected():
            self.log(1, "Already connected")
            return None

        self.log(2, "Connecting to " + self.indi_server_ip + ":" + str(self.indi_port))
        self.indiclient.setServer(self.indi_server_ip, self.indi_port)

        if not (self.indiclient.connectServer()):
            self.log(0, "Connection error")
            return None

        if self.ui is not None:
            self.ui.connected()
        self.log(2, "Connected")

    def disconnect(self):
        if not self.is_connected():
            self.log(1, "Already disconnected")
            return None

        if self.tracking:
            self.stop_tracking()

        if not (self.indiclient.disconnectServer()):
            self.log(0, "Error during disconnection")
            return None

        if self.ui is not None:
            self.ui.disconnected()

        self.log(2, "Disconnection successful")

    def is_connected(self):
        return self.indiclient.isServerConnected()

    def setUI(self, ui):
        self.ui = ui

    # Tracking
    def start_tracking(self):
        # TODO
        if not self.indiclient.telescope_features["minimal"]:
            self.log(0, "Tracking cannot be started: no telescope connected")
            return

        self.tracking = True
        if self.ui is not None:
            self.ui.tracking_started()

    def stop_tracking(self):
        # TODO
        self.tracking = False
        self.indiclient.set_speed(0, 0)
        if self.ui is not None:
            self.ui.tracking_stopped()

    def update_tracking(self, current_ra, current_dec):
        # This procedure is called each time the telescope coordinates are updated
        # TODO
        if not self.tracking:
            return

        target_ra, target_dec, alt = self.sat_pos()
        target_ra_1, target_dec_1, alt = self.sat_pos(self.ts.tt(jd=self.t().tt + 1. / 86400.)) # at t + 1s

        # perform all calculations in deg
        diff_ra = target_ra._degrees - current_ra * 15
        diff_dec = target_dec._degrees - current_dec
        target_speed_ra = target_ra_1._degrees - target_ra._degrees
        target_speed_dec = target_dec_1._degrees - target_dec._degrees

        speed_ra = self.p_gain * diff_ra + target_speed_ra
        speed_dec = self.p_gain * diff_dec + target_speed_dec

        self.log(3,
                 "\ntime: {0}\ntarget:{1} / {2}\ncurrent: {3} / {4}\ndiff: {5} / {6}\ntarget speed: {7} / {8}\ncommand speec: {9} / {10}".format(
                     self.t_iso(), target_ra, target_dec, Angle(hours=current_ra), Angle(degrees=current_dec),
                     Angle(degrees=diff_ra), Angle(degrees=diff_dec), target_speed_ra, target_speed_dec, speed_ra,
                     speed_dec))

        if speed_ra > self.max_rate:
            speed_ra = self.max_rate
        if speed_dec > self.max_rate:
            speed_dec = self.max_rate
        if speed_ra < -self.max_rate:
            speed_ra = -self.max_rate
        if speed_dec < -self.max_rate:
            speed_dec = -self.max_rate

        self.indiclient.set_speed(speed_ra, speed_dec)


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
            "TELESCOPE_MOTION_NS": None,
            "TELESCOPE_MOTION_WE": None,
            "TELESCOPE_TIMED_GUIDE_NS": None,
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

    def newDevice(self, d):
        self.st.log(2, "New device: " + d.getDeviceName())

        if d.getDeviceName() == "Joystick":
            self.st.ui.add_joystick()
            self.joystick = d
        else:
            self.st.ui.add_telescope(d.getDeviceName())

    def newProperty(self, p):
        if p.getDeviceName() == self.telescope_name:
            if p.getName() in self.telescope_prop.keys():
                self.telescope_prop[p.getName()] = p
                self.update_telescope_features()

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
            "TELESCOPE_MOTION_NS": None,
            "TELESCOPE_MOTION_WE": None,
            "TELESCOPE_TIMED_GUIDE_NS": None,
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
        # - Move: TELESCOPE_MOTION_NS, TELESCOPE_MOTION_WE
        # - Timed move: TELESCOPE_TIMED_GUIDE_NS, TELESCOPE_TIMED_GUIDE_WE
        # - Speed: TELESCOPE_CURRENT_RATE
        # - Other: TELESCOPE_SLEW_RATE, TELESCOPE_PIER_SIDE

        t = 0
        while not (self.telescope_features["minimal"] & (
                self.telescope_features["move"] or self.telescope_features["timed"] or self.telescope_features[
            "speed"])):
            if t > self.st.connection_timeout:
                self.st.log(0,
                            "Error during driver connection: No control method available, Is \"" + device_name + "\" a telescope device ?")
                return False
            time.sleep(0.05)
            t = t + 0.05

        self.update_telescope_features()
        self.st.log(2, device_name + " connected")
        return True

    def update_telescope_features(self):
        telescope_requirements = {
            "minimal": {"CONNECTION", "EQUATORIAL_EOD_COORD", "ON_COORD_SET"},
            "move": {"TELESCOPE_MOTION_NS", "TELESCOPE_MOTION_WE"},
            "timed": {"TELESCOPE_TIMED_GUIDE_NS", "TELESCOPE_TIMED_GUIDE_WE"},
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

        ra_speed = ra_speed /360 * 86164.1
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


class CatalogItem(object):
    """ Satellite catalog item """

    def __init__(self, name, url, active=False):
        self.name = name
        self.url = url
        self.active = active


class Error(Exception):
    pass
