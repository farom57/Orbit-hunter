"""
Author: Romain Fafet (farom57@gmail.com)
"""

from sattrack import *
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindow import Ui_MainWindow
from timedialog import Ui_Timedialog
from threading import Timer



class UI(QtWidgets.QMainWindow,  Ui_MainWindow):
    """ User interface of pySatTrack """

    def __init__(self,st):
        super(UI, self).__init__()
        self.st = st
        self.st.setUI(self)

        self.setupUi(self)

        # Slot connect to internal functions
        self.connectButton.clicked.connect(self.connect_clicked)
        self.telescopeComboBox.currentIndexChanged['QString'].connect(self.telescope_changed)
        self.joystickCheckBox.stateChanged.connect(self.joystick_changed)

        self.trackingComboBox.currentIndexChanged['QString'].connect(self.trackmode_changed)
        self.pGainSpinBox.valueChanged['double'].connect(self.trackparam_changed)
        self.tauISpinBox.valueChanged['double'].connect(self.trackparam_changed)
        self.tauDSpinBox.valueChanged['double'].connect(self.trackparam_changed)
        self.maxRateSpinBox.valueChanged['double'].connect(self.trackparam_changed)
        self.saturationSpinBox.valueChanged['double'].connect(self.trackparam_changed)
        self.trackButton.clicked.connect(self.track_clicked)

        self.latitudeEdit.textChanged.connect(self.location_changed)
        self.longitudeEdit.textChanged.connect(self.location_changed)
        self.altitudeSpinBox.valueChanged['int'].connect(self.location_changed)

        self.realTimeButton.toggled['bool'].connect(self.timemode_changed)
        self.setTimeButton.clicked.connect(self.settime_clicked)

        self.catalogSatButton.toggled['bool'].connect(self.satmode_changed)
        self.satComboBox.currentIndexChanged['QString'].connect(self.satellite_changed)
        self.catalogConfigButton.clicked.connect(self.catconfig_clicked)
        self.tleEdit.textChanged.connect(self.tle_changed)

        # Additionnal slot connection to grey out widged depending on optionbox
        self.realTimeButton.toggled['bool'].connect(self.setTimeButton.setDisabled)
        self.catalogSatButton.toggled['bool'].connect(self.satComboBox.setEnabled)
        self.catalogSatButton.toggled['bool'].connect(self.catalogConfigButton.setEnabled)
        self.catalogSatButton.toggled['bool'].connect(self.tleEdit.setDisabled)


        # timer to update the time:
        self.timer=Timer(1., self.update_time)
        self.timer.start()



# Buttons

    def connect_clicked(self):
        if self.st.is_connected():
            self.st.disconnect()
        else:
            self.st.connect()

    def track_clicked(self):
        self.st.log(1, 'track_btn_cmd not yet implemented')

    def settime_clicked(self):
        self.timedg=Timedialog(self.st)
        self.timedg.show_modal()

    def catconfig_clicked(self):
        self.st.log(1, 'catconfig_btn_cmd not yet implemented')

# Values entered callbacks
    def timemode_changed(self, realtime):
        if realtime:
            self.st.observer_offset=0

    def satmode_changed(self, catalog):
        self.st.log(1, 'indi_telescope_chg not yet implemented')

    def telescope_changed(self, driver):
        self.st.log(1, 'indi_telescope_chg not yet implemented')

    def joystick_changed(self, enabled):
        self.st.log(1, 'indi_joystick_chg not yet implemented')

    def satellite_changed(self):
        #self.sat_TLE_txt.delete('1.0', 'end')
        #self.st.selected_satellite = self.sat_list.get()
        #self.sat_TLE_txt.insert('1.0', self.st.selected_satellite + ' is selected')
        self.st.log(1, 'sat_chg not yet implemented')

    def tle_changed(self):
        self.st.log(1, 'sat_chg_cmd not yet implemented')

    def location_changed(self):
        #try:
        #self.st.observer_alt = self.obs_alt_var.get()
        #self.st.observer_lat = self.obs_lat_var.get()
        #self.st.observer_lon = self.obs_lon_var.get()
        #    self.obs_loc_str.set("Valid location")
        #except ValueError:
        #    self.obs_loc_str.set("Invalid location")
        self.st.log(1, 'not yet implemented')

    def trackmode_changed(self, mode):
        self.st.log(1, 'trackmode_changed not yet implemented')

    def trackparam_changed(self,  dummy):
        self.st.log(1, 'trackparam_changed not yet implemented')

# System callbacks
    def connected(self):
        self.indi_connect_var.set("Disconnect")
        self.indi_status_var.set("Connected but driver not configured")
    def disconnected(self):
        self.indi_connect_var.set("Connect")
        self.indi_status_var.set("Not connected")
        self.indi_telescope_options = ("None", )
        self.indi_telescope_var.set(self.indi_telescope_options[0])
    def addTelescope(self, device_name):
        if self.indi_telescope_options[0]=="None":
            self.indi_telescope_options[0]=device_name
        else:
            self.indi_telescope_options.append(device_name)
        self.indi_telescope.config(items = self.indi_telescope_options)
        self.indi_telescope_var.set(self.indi_telescope_options[0])

# 1sec update (time & sat location)
    def update_time(self):
        self.timeLabel.setText(self.st.t_iso())
        self.timer=Timer(1., self.update_time)
        self.timer.start()

class Timedialog(QtWidgets.QDialog,  Ui_Timedialog):
    """ Dialog to set simulation time """

    def __init__(self, st):
        super(Timedialog, self).__init__()
        self.st=st
        self.setupUi(self)

        datetime = QtCore.QDateTime.fromString(self.st.t_iso(), "yyyy-MM-ddTHH:mm:ssZ")
        datetime.setOffsetFromUtc(0)
        self.dateTimeEdit.setDateTime(datetime)

        self.buttonBox.accepted.connect(self.settime)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def settime(self):
        self.st.log(1, self.st.observer_offset)
        self.st.set_time(
            self.dateTimeEdit.date().year(),
            self.dateTimeEdit.date().month(),
            self.dateTimeEdit.date().day(),
            self.dateTimeEdit.time().hour(),
            self.dateTimeEdit.time().minute(),
            self.dateTimeEdit.time().second())
        self.st.log(1, self.st.observer_offset)


    def show_modal(self):
        self.setModal(True)
        self.show()
