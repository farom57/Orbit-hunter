"""
Author: Romain Fafet (farom57@gmail.com)
"""

from sattrack import *
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindow import Ui_MainWindow
from timedialog import Ui_Timedialog
from catalogdialog import Ui_Catalogdialog
from threading import Timer



class UI(QtWidgets.QMainWindow,  Ui_MainWindow):
    """ User interface of pySatTrack """

    def __init__(self,st):
        super(UI, self).__init__()
        self.st = st
        self.st.setUI(self)

        self.setupUi(self)

        # Load dynamic content
        self.hostEdit.setText(self.st.indi_server)
        self.portEdit.setValue(self.st.indi_port)
        self.trackingComboBox.setCurrentIndex(self.st.track_method)
        self.pGainSpinBox.setValue(self.st.p_gain)
        self.tauISpinBox.setValue(self.st.tau_i)
        self.tauDSpinBox.setValue(self.st.tau_d)
        self.maxRateSpinBox.setValue(self.st.max_rate)
        self.saturationSpinBox.setValue(self.st.i_sat)
        self.latitudeEdit.setText(self.st.observer_lat)
        self.longitudeEdit.setText(self.st.observer_lon)
        self.altitudeSpinBox.setValue(self.st.observer_alt)
        self.update_sat_list()

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
        self.catdg=Catalogdialog(self.st)
        self.catdg.show_modal()

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

    def satellite_changed(self, name):
        self.st.selected_satellite = name
        age = self.st.t() - self.st.sat.epoch
        self.satLabel.setText('Valid elements, ' + '{:.2f} days old'.format(age))
        self.st.log(1, 'Satellite changed: '+name)

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
        """ when INDI connection is established"""
        self.indi_connect_var.set("Disconnect")
        self.indi_status_var.set("Connected but driver not configured")
    def disconnected(self):
        """ when INDI connection is ended"""
        self.indi_connect_var.set("Connect")
        self.indi_status_var.set("Not connected")
        self.indi_telescope_options = ("None", )
        self.indi_telescope_var.set(self.indi_telescope_options[0])
    def addTelescope(self, device_name):
        """ when INDI driver is detected"""
        if self.indi_telescope_options[0]=="None":
            self.indi_telescope_options[0]=device_name
        else:
            self.indi_telescope_options.append(device_name)
        self.indi_telescope.config(items = self.indi_telescope_options)
        self.indi_telescope_var.set(self.indi_telescope_options[0])
    def update_sat_list(self):
        """ when satellite list shell be updated"""
        # build & sort key list
        keys=[]
        for key in self.st.satellites_tle:
            keys.append(str(key))
        keys.sort()

        # update the combobox
        self.satComboBox.clear()
        for key in keys:
            self.satComboBox.addItem(str(key))

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

        # UI setup
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.settime)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # set initial date to now
        datetime = QtCore.QDateTime.fromString(self.st.t_iso(), "yyyy-MM-ddTHH:mm:ssZ")
        datetime.setOffsetFromUtc(0)
        self.dateTimeEdit.setDateTime(datetime)


    def settime(self):
        """ Called when OK button pressed """
        self.st.set_time(
            self.dateTimeEdit.date().year(),
            self.dateTimeEdit.date().month(),
            self.dateTimeEdit.date().day(),
            self.dateTimeEdit.time().hour(),
            self.dateTimeEdit.time().minute(),
            self.dateTimeEdit.time().second())


    def show_modal(self):
        self.setModal(True)
        self.show()

class Catalogdialog(QtWidgets.QDialog,  Ui_Catalogdialog):
    """ Dialog to set satellite catalog """

    def __init__(self, st):
        super(Catalogdialog, self).__init__()
        self.st=st

        # UI setup
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.setcatalog)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Populate list widget
        for catalog in self.st.catalogs:
            item = QtWidgets.QListWidgetItem()
            item.setText(catalog.name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if catalog.active:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            self.listWidget.addItem(item)

    def setcatalog(self):
        """ Update catalog checked states """
        i=0
        for catalog in self.st.catalogs:
            if self.listWidget.item(i).checkState()==QtCore.Qt.Checked:
                catalog.active=True
            else:
                catalog.active=False
            i=i+1
        self.st.update_tle()


    def show_modal(self):
        self.setModal(True)
        self.show()


