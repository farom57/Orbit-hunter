"""
Author: Romain Fafet (farom57@gmail.com)
"""
from skyfield.api import load, Topos, Star, EarthSatellite
from skyfield.positionlib import Geocentric, ICRF
from skyfield.units import Angle
from numpy import cos, sin, arccos, arcsin, arctan2, pi, einsum, sqrt
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
            CatalogItem("SES", "https://celestrak.com/NORAD/elements/ses.txt", True),
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
        planets = load('de421.bsp')
        self.earth = planets['earth']
        self.sun = planets['sun']

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

    def scalar_product(self, a, b):
        return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

    def illuminated(self, t=None):
        """ return false if the satellite is in shadow """
        if t is None:
            t = self.t()

        # projection of the earth center on the ray between the sun and the satellite
        earth_sat_vect = (self.sat).at(t).position.au
        sun_sat_vect = (self.sat - (self.sun - self.earth)).at(t).position.au
        product = self.scalar_product(earth_sat_vect,sun_sat_vect)

        if product < 0:     # The satellite is in front of the earth
            return True
        else:               # The satellite is after the earth, let's check if the ray is underground
            sun_sat_vect = sun_sat_vect / sqrt(self.scalar_product(sun_sat_vect,sun_sat_vect)) # normalize
            earth_projection_vect = earth_sat_vect - self.scalar_product(earth_sat_vect,sun_sat_vect) * sun_sat_vect
            earth_projection = Geocentric(position_au=earth_projection_vect,center=399,t=t)
            return earth_projection.subpoint().elevation.m>0.

    def in_shadow(self, t=None):
        return not self.illuminated(t)

    def telescope_pos(self):
        """ Telescope position: ra, dec """
        if self.indiclient.telescope_features["minimal"]:
            radec = self.indiclient.telescope.getNumber("EQUATORIAL_EOD_COORD")
            star = Star(ra_hours=radec[0].value, dec_degrees=radec[1].value)
            # alt, az = self.obs.at(self.t()).observe(star).apparent().altaz()
            return star.ra, star.dec
        else:
            raise Error("Unable to get the coordinates from the telescope")

    def radec2altaz(self, ra, dec, t=None):
        """
        Convert ra,dec in alt,az
        :param ra: ra in rad
        :param dec: dec in rad
        :param t: Skyfield Time object, use current time if omitted
        :return: alt, az in rad
        """
        if t is None:
            t = self.t()
        rot = self.obs._altaz_rotation(t)
        cosdec = cos(dec)
        radec = [cosdec * cos(ra), cosdec * sin(ra), sin(dec)]
        altaz = einsum("ij,j->i", rot, radec)
        alt = arcsin(altaz[2])
        az = arctan2(altaz[1], altaz[0])
        return alt, az

    def radec2altaz_2(self, ra, dec, t=None):
        """
        Convert ra,dec in alt,az
        :param ra: ra as skyfield Angle object
        :param dec: dec as skyfield Angle object
        :param t: Skyfield Time object, use current time if omitted
        :return: alt, az as skyfield Angle object
        """
        alt,az=self.radec2altaz(ra.radians, dec.radians, t)
        return Angle(radians=alt, preference="degrees"), Angle(radians=az, preference="degrees")

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
        if self.ui is not None:
            if level == 0:
                print("ERROR: " + text)
                self.ui.logBrowser.append("<font color=\"Red\">{0} - ERROR: {1}</font>".format(self.t_iso(), text))
            elif level == 1:
                print("WARNING: " + text)
                self.ui.logBrowser.append("<font color=\"Orange\">{0} - WARNING: {1}</font>".format(self.t_iso(), text))
            elif level == 2:
                print("Info: " + text)
                self.ui.logBrowser.append("<font color=\"Black\">{0} - Info: {1}</font>".format(self.t_iso(), text))
            else:
                pass
                # self.ui.logBrowser.append("<font color=\"Blue\">{0} - Debug: {1}</font>".format(self.t_iso(), text))

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

    # next pass prediction
    def next_pass(self, t0, backward=False):
        """
        Predict the next pass. Return a tuple containing the dates and alt az angles of the rise, culmination, meridian crossing and set, or None if the respective event does no happen.
        Return ((None,None, None, None, t0),(None,None, None, None),(None,None, None, None)) if no pass is found.

        :param t0: time to start the search
        :param backward: backward = True will search the previous pass
        :return: ((t_rise, t_culmination, t_meridian, t_set, t0), (alt_rise, alt_culmination, alt_meridian, alt_set), (az_rise, az_culmination, az_meridian, az_set))
        """
        t0 = t0.tt

        def alt_t(dt):
            tjd = t0 + dt / 86400
            ra, dec, dist = self.sat_pos(t=self.ts.tt(jd=tjd))
            alt, az = self.radec2altaz(ra.radians, dec.radians, t=self.ts.tt(jd=tjd))
            return alt

        def az_t(dt):
            tjd = t0 + dt / 86400
            ra, dec, dist = self.sat_pos(t=self.ts.tt(jd=tjd))
            alt, az = self.radec2altaz(ra.radians, dec.radians, t=self.ts.tt(jd=tjd))
            return az

        dir = -1 if backward else 1
        step = 60 * 20  # less than 1/4 of orbit
        small_step = 30  # few deg
        smaller_step = 1  # time resolution
        trajectory_segments = 20
        dt0 = 0
        dt_rise = None
        dt_set = None
        dt_meridian = None
        dt_culmination = None

        while True:
            # Ascending / descending orbit coarse detection
            alt0 = alt_t(dt0)
            alt1 = alt_t(dt0 + step * dir)
            while alt1 < alt0  and dt0 * dir < 86400 and alt1 < 0:
                self.log(3, "Phase 1: Decreasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
                alt0 = alt1
                dt0 = dt0 + step * dir
                alt1 = alt_t(dt0 + step * dir)

            while alt1 >= alt0 and dt0 * dir < 86400:
                self.log(3, "Phase 1: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
                alt0 = alt1
                dt0 = dt0 + step * dir
                alt1 = alt_t(dt0 + step * dir)

            if dt0 * dir > 86400 and alt1 < 0:
                self.log(2, "no other pass for today")
                return ((None, None, None, None, t0), (None, None, None, None), (None, None, None, None))

            self.log(3, "Phase 1: Maximum between dt0={0} and {1}".format(dt0 - step * dir, dt0 + step * dir))
            dt0 = dt0 - step * dir
            alt0 = alt_t(dt0)
            alt1 = alt_t(dt0 + small_step * dir)

            # Refining the maximum altitude
            while alt1 >= alt0 and alt1 < 10 and dt0 * dir < 86400:
                self.log(3, "Phase 2: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
                alt0 = alt1
                dt0 = dt0 + small_step * dir
                alt1 = alt_t(dt0 + small_step * dir)

            if (alt1 < 0):
                if dt0 * dir < 86400:
                    continue  # restart the search for the following orbit
                else:
                    self.log(2, "no pass found")
                    return ((None, None, None, None, t0), (None, None, None, None), (None, None, None, None))
            else:
                # Refining a 2nd time the maximum altitude to get the date
                alt1 = alt_t(dt0 + smaller_step * dir)
                while alt1 >= alt0:
                    if dt0 * dir > 86400:
                        self.log(3, "no culmination today")
                        return ((None, None, None, None, t0), (None, None, None, None), (None, None, None, None))
                    self.log(3, "Phase 3: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
                    alt0 = alt1
                    dt0 = dt0 + smaller_step * dir
                    alt1 = alt_t(dt0 + smaller_step * dir)
                dt_culmination = dt0

                # refining rise and set date by dichotomy
                # set
                dt0 = dt_culmination
                alt0 = alt_t(dt_culmination)
                alt1 = alt_t(dt_culmination + step)
                while alt1 >= 0 and dt0 < 86400:
                    self.log(3, "Phase 4 set: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
                    alt0 = alt1
                    dt0 = dt0 + step
                    alt1 = alt_t(dt0 + step)
                if dt0 > 86400:
                    self.log(3, "no set today")
                else:
                    dt1 = dt0 + step
                    while dt1 - dt0 > smaller_step:
                        dt2 = (dt0 + dt1) / 2
                        alt2 = alt_t(dt2)

                        if alt2 > 0:
                            dt0 = dt2
                            alt0 = alt2
                        else:
                            dt1 = dt2
                            alt1 = alt2
                        self.log(3,
                                 "Phase 4 set: Restrict set date to dt={0} alt={1} to dt={2} alt={3}".format(dt0, alt0,
                                                                                                             dt1,
                                                                                                             alt1))
                    dt_set = dt0

                # rise
                dt0 = dt_culmination
                alt0 = alt_t(dt_culmination)
                alt1 = alt_t(dt_culmination - step)
                while alt1 >= 0 and dt0 > -86400:
                    self.log(3, "Phase 4 rise: Increasing at dt0={0}, alt0={1}, alt1={2}".format(dt0, alt0, alt1))
                    alt0 = alt1
                    dt0 = dt0 - step
                    alt1 = alt_t(dt0 - step)
                if dt0 < -86400:
                    self.log(3, "no rise today")
                else:
                    dt1 = dt0 - step
                    while dt0 - dt1 > smaller_step:
                        dt2 = (dt0 + dt1) / 2
                        alt2 = alt_t(dt2)
                        if alt2 > 0:
                            dt0 = dt2
                            alt0 = alt2
                        else:
                            dt1 = dt2
                            alt1 = alt2
                        self.log(3,
                                 "Phase 4 rise: Restrict set date to dt={0} alt={1} to dt={2} alt={3}".format(dt0, alt0,
                                                                                                              dt1,
                                                                                                              alt1))
                    dt_rise = dt0

                # meridian
                if (dt_rise is not None) and (dt_set is not None):
                    dt0 = dt_rise
                    dt1 = dt0 + (dt_set - dt_rise) / trajectory_segments
                    az0 = az_t(dt0)
                    az1 = az_t(dt1)
                    while dt1 < dt_set and az0 * az1 > 0:  # equivalent to sign(az0)==sign(az1)
                        dt0 = dt1
                        dt1 = dt0 + (dt_set - dt_rise) / trajectory_segments
                        az0 = az1
                        az1 = az_t(dt1)
                        self.log(3,
                                 "Phase 5a: Segment dt={0} az={1} to dt={2} az={3}".format(dt0, az0, dt1, az1))
                    if dt1 >= dt_set:
                        self.log(3, "no meridian crossing")
                    else:
                        while dt1 - dt0 > smaller_step:
                            dt2 = (dt0 + dt1) / 2
                            az2 = az_t(dt2)
                            if az2 * az0 > 0:
                                dt0 = dt2
                                az0 = az2
                            else:
                                dt1 = dt2
                                az1 = az2
                            self.log(3,
                                     "Phase 5b: Restrict meridian crossing date to dt={0} az={1} to dt={2} az={3}".format(
                                         dt0,
                                         az0,
                                         dt1,
                                         az1))
                        dt_meridian = dt0

                if dt_rise is not None:
                    t_rise = self.ts.tt(jd=t0 + dt_rise / 86400)
                    alt_rise = Angle(radians=alt_t(dt_rise), preference="degrees")
                    az_rise = Angle(radians=az_t(dt_rise), preference="degrees")
                else:
                    t_rise = None
                    alt_rise = None
                    az_rise = None

                if dt_culmination is not None:
                    t_culmination = self.ts.tt(jd=t0 + dt_culmination / 86400)
                    alt_culmination = Angle(radians=alt_t(dt_culmination), preference="degrees")
                    az_culmination = Angle(radians=az_t(dt_culmination), preference="degrees")
                else:
                    t_culmination = None
                    alt_culmination = None
                    az_culmination = None

                if dt_meridian is not None:
                    t_meridian = self.ts.tt(jd=t0 + dt_meridian / 86400)
                    alt_meridian = Angle(radians=alt_t(dt_meridian), preference="degrees")
                    az_meridian = Angle(radians=az_t(dt_meridian), preference="degrees")
                else:
                    t_meridian = None
                    alt_meridian = None
                    az_meridian = None

                if dt_set is not None:
                    t_set = self.ts.tt(jd=t0 + dt_set / 86400)
                    alt_set = Angle(radians=alt_t(dt_set), preference="degrees")
                    az_set = Angle(radians=az_t(dt_set), preference="degrees")
                else:
                    t_set = None
                    alt_set = None
                    az_set = None

                self.log(2,
                         "pass found:\n rise: dt={0} az={1}\n meridian:  dt={2} az={3} alt={4}\n culmination:  dt={5} az={6} alt={7}\n set: dt={8} az={9}".format(
                             dt_rise, az_rise, dt_meridian, az_meridian, alt_meridian, dt_culmination,
                             az_culmination,
                             alt_culmination, dt_set, az_set))

                return ((t_rise, t_culmination, t_meridian, t_set, t0), (alt_rise, alt_culmination, alt_meridian, alt_set),
                        (az_rise, az_culmination, az_meridian, az_set))

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
        target_ra_1, target_dec_1, alt = self.sat_pos(self.ts.tt(jd=self.t().tt + 1. / 86400.))  # at t + 1s

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


class CatalogItem(object):
    """ Satellite catalog item """

    def __init__(self, name, url, active=False):
        self.name = name
        self.url = url
        self.active = active


class Error(Exception):
    pass
