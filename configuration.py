"""
Author: Romain Fafet (farom57@gmail.com)
"""
from skyfield.api import load

class Configuration(object):
    """ A Configuration store all the settings for the Tracker.

    Those settings can be edited through the UI. Configuration class also
    provide functions to load and save itself on a file
    """
    def __init__(self):
        self.indi_server_ip = "127.0.0.1"
        self.indi_port = 7624
        self.indi_telescope_driver = ""
        self.indi_joystick_driver = ""

        self.satellites_url = "http://celestrak.com/NORAD/elements/stations.txt"
        self.selected_satellite = 'ISS (ZARYA)'
        self.satellites_tle = load.tle(self.satellites_url)


        ts = load.timescale()
        t = ts.now()
        days = t - self.satellites_tle[self.selected_satellite].epoch
        print('{:.3f} days away from epoch'.format(days))
        if abs(days) > 14:
            self.satellites_tle = load.tle(self.satellites_url, reload=True)

        self.observer_alt = 5
        self.observer_lat = "43.538 N"
        self.observer_lon = "6.955 E"
        self.observer_offset = 0 # in minutes

        self.track_method = "Speed"

        self.p_gain = 0.5
        self.tau_i = 3
        self.tau_d = 1
        self.max_rate = 200
        self.i_sat = 0.5


