"""
Author: Romain Fafet (farom57@gmail.com)
"""
from skyfield.api import load, Topos

class Configuration(object):
    """ A Configuration store all the settings for the Tracker.

    Those settings can be edited through the UI. Configuration class also
    provide functions to load and save itself on a file
    """
    def __init__(self):

    # savable variables
        self.indi_server_ip = "127.0.0.1"
        self.indi_port = 7624
        self.indi_telescope_driver = ""
        self.indi_joystick_driver = ""

        self.satellites_url = "http://celestrak.com/NORAD/elements/stations.txt"
        self._selected_satellite = 'ISS (ZARYA)'

        self._observer_alt = 5
        self._observer_lat = "43.538 N"
        self._observer_lon = "6.955 E"
        self._observer_offset = 0 # in days

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

    def t(self):
        tmp=self.ts.now().tt + self._observer_offset
        return self.ts.tt(jd=tmp)

    def t_iso(self):
        tmp=self.ts.now().tt + self.observer_offset
        return self.ts.tt(jd=tmp).utc_iso()

    def _set_selected_satellite(self, n_sat):
        self._selected_satellite = n_sat
        self.sat = self.satellites_tle[self._selected_satellite] # TODO: add error management

    def _set_observer_alt(self,  n_alt):
        self._observer_alt=n_alt
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)

    def _set_observer_lat(self, n_lat):
        self._observer_lat=n_lat
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)

    def _set_observer_lon(self, n_lon):
        self._observer_lon=n_lon
        self.obs = Topos(self._observer_lat, self._observer_lon, None, None, self._observer_alt)

    def get_sat_pos(self):
        diff = self.sat - self.obs
        topocentric = diff.at(self.t())
        alt, az, distance = topocentric.altaz()
        ra, dec = topocentric.radec()
        return ra, dec, alt, az, distance
