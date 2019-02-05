"""
Author: Romain Fafet (farom57@gmail.com)
"""
from skyfield.api import load, Topos

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

        self.satellites_url = "http://celestrak.com/NORAD/elements/stations.txt"
        self._selected_satellite = 'ISS (ZARYA)'

        self._observer_alt = 5
        self._observer_lat = "43.538 N"
        self._observer_lon = "6.955 E"
        self.observer_offset = 0 # in days

        self.track_method = "Speed"

        self.p_gain = 0.5
        self.tau_i = 3
        self.tau_d = 1
        self.max_rate = 200
        self.i_sat = 0.5

    # dynamic data
        self.ts = load.timescale()
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)


        # reload TLE if old data
        self.satellites_tle = load.tle(self.satellites_url) # TODO: add error management
        age = self.t() - self.satellites_tle[self._selected_satellite].epoch
        print('{:.3f} days away from epoch'.format(age))
        if abs(age) > 3:
            self.satellites_tle = load.tle(self.satellites_url, reload=True)
        self.sat = self.satellites_tle[self._selected_satellite] # TODO: add error management



    # Some properties to maintain to preserve internal consistency when attributes are updated and for error management
    @property
    def selected_satellite(self):
        return self._selected_satellite
    @selected_satellite.setter
    def selected_satellite(self, n_sat):
        self._selected_satellite = n_sat
        self.sat = self.satellites_tle[self._selected_satellite] # TODO: add error management
    @property
    def observer_alt(self):
        return self._observer_alt
    @observer_alt.setter
    def observer_alt(self,  n_alt):
        self._observer_alt=n_alt
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)

    @property
    def observer_lat(self):
        return self._observer_lat
    @observer_lat.setter
    def observer_lat(self,  n_lat):
        self._observer_lat=n_lat
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)# TODO: add error management

    @property
    def observer_lon(self):
        return self._observer_lon
    @observer_lon.setter
    def observer_lon(self,  n_lon):
        self._observer_lon=n_lon
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
        tmp=self.ts.now().tt + self.observer_offset
        return self.ts.tt(jd=tmp)

    def t_iso(self):
        tmp=self.ts.now().tt + self.observer_offset
        return self.ts.tt(jd=tmp).utc_iso()
