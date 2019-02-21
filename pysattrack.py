"""
pySatTrack allows you to track satellites with any INDI telescope

Author: Romain Fafet (farom57@gmail.com)
"""

from sattrack import *
from ui import *

# TODO: load existing configuration if any
st = SatTrack()
app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
ui = UI(st)
ui.show()
app.exec_()
# TODO: st.save()
