"""
pySatTrack allows you to track satellites with any INDI telescope

Author: Romain Fafet (farom57@gmail.com)
"""

from configuration import *
from tracker import *
from ui import *

# TODO: load existing configuration if any
conf = Configuration()
tracker = Tracker(conf)
ui = UI(tracker) # infinite loop until it quits
# TODO: conf.save()
