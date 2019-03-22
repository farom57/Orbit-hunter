"""
Author: Romain Fafet (farom57@gmail.com)
"""
from skyfield.api import load, Topos
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
        self.max_rate = 200
        self.i_sat = 0.5

        self.connection_timeout = 1

        # dynamic data
        self.ui = None
        self.indiclient = IndiClient(self)
        self.ts = load.timescale()
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)
        self.update_tle()

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

    @property
    def observer_alt(self):
        return self._observer_alt

    @observer_alt.setter
    def observer_alt(self, n_alt):
        self._observer_alt = n_alt
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)

    @property
    def observer_lat(self):
        return self._observer_lat

    @observer_lat.setter
    def observer_lat(self, n_lat):
        self._observer_lat = n_lat
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None,
                         self._observer_alt)  # TODO: add error management

    @property
    def observer_lon(self):
        return self._observer_lon

    @observer_lon.setter
    def observer_lon(self, n_lon):
        self._observer_lon = n_lon
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)

    # Utility functions
    def sat_pos(self):
        """ Satellite position: ra, dec, alt, az, distance"""
        diff = self.sat - self.obs
        topocentric = diff.at(self.t())
        alt, az, distance = topocentric.altaz()
        ra, dec = topocentric.radec()
        return ra, dec, alt, az, distance

    def t(self):
        """ Current sofware time"""
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

    def update_tle(self, max_age=3):
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
        pass

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
        self.st.log(0, "Connection lost")

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

        # Check existing properties (new ones will be detected later by newProperty())
        for key in self.telescope_prop:
            prop = self.telescope.getProperty(key)
            if prop:
                self.telescope_prop[key]=prop

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
        while not(self.telescope_features["minimal"] & (self.telescope_features["move"] or self.telescope_features["timed"] or self.telescope_features["speed"])):
            if t > self.st.connection_timeout:
                self.st.log(0, "Error during driver connection: No control method available, Is \"" + device_name + "\" a telescope device ?")
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


class CatalogItem(object):
    """ Satellite catalog item """

    def __init__(self, name, url, active=False):
        self.name = name
        self.url = url
        self.active = active
