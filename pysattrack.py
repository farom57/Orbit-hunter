"""
pySatTrack allows you to track satellites with any INDI telescope

Author: Romain Fafet (farom57@gmail.com)
"""

from sattrack import *
from ui import *

# TODO: load existing configuration if any
st = SatTrack()
ui = UI(st) # infinite loop until it quits
# TODO: st.save()
