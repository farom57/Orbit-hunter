"""
Author: Romain Fafet (farom57@gmail.com)
"""

from configuration import *
from ui import *
#from indiclient import *

class Tracker(object):
    """ The Tracker class perform the satellite tracking

    The tracker must be initialized with a Configuration object. It can be
    controlled through connect, disconnect, start, stop and
    goto_rise_location_and_wait function. It can also report the tracking status
    to an ui.
    """

    def __init__(self, conf):
        self.conf = conf

    def register_ui(self,  ui):
        self.ui = ui
