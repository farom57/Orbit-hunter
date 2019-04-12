"""
Author: Romain Fafet (farom57@gmail.com)
"""

from PyQt5 import QtCore, QtWidgets
from mainwindow import Ui_MainWindow
from timedialog import Ui_Timedialog
from catalogdialog import Ui_Catalogdialog
from sattrack import Error




class UI(QtWidgets.QMainWindow, Ui_MainWindow):
    """ User interface of pySatTrack """

    def __init__(self, st):
        super(UI, self).__init__()
        self.st = st # type: SatTrack
        self.st.setUI(self)

        self.setupUi(self)

        # Load dynamic content
        self.hostEdit.setText(self.st.indi_server_ip)
        self.portEdit.setValue(self.st.indi_port)
        self.indiLabel.setText("Not connected")
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
        self.hostEdit.textChanged.connect(self.connection_info_changed)
        self.portEdit.valueChanged.connect(self.connection_info_changed)

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
        self.enable_satellite_changed = True
        self.catalogConfigButton.clicked.connect(self.catconfig_clicked)
        self.tleEdit.textChanged.connect(self.tle_changed)

        # Additional slot connection to grey out widget depending on optionbox
        self.realTimeButton.toggled['bool'].connect(self.setTimeButton.setDisabled)
        self.catalogSatButton.toggled['bool'].connect(self.satComboBox.setEnabled)
        self.catalogSatButton.toggled['bool'].connect(self.catalogConfigButton.setEnabled)
        self.catalogSatButton.toggled['bool'].connect(self.tleEdit.setDisabled)

        # Other init
        self.indi_telescope_options = ["None"]

        # timer to update the time:
        self.startTimer(1000)

    # Buttons
    def connect_clicked(self):
        if self.st.is_connected():
            self.st.disconnect()
        else:
            self.st.connect()

    def track_clicked(self):
        if not self.st.tracking:
            self.st.start_tracking()
        else:
            self.st.stop_tracking()

    def settime_clicked(self):
        self.timedg = Timedialog(self.st)
        self.timedg.show_modal()

    def catconfig_clicked(self):
        self.catdg = Catalogdialog(self.st)
        self.catdg.show_modal()

    # Values entered callbacks
    def connection_info_changed(self):
        self.st.indi_server_ip=self.hostEdit.text()
        self.st.indi_port=self.portEdit.value()

    def timemode_changed(self, realtime):
        if realtime:
            self.st.observer_offset = 0

    def satmode_changed(self, catalog):
        self.st.log(1, 'indi_telescope_chg not yet implemented')

    def telescope_changed(self, driver):
        self.st.indiclient.set_telescope(driver)

    def joystick_changed(self, enabled):
        self.st.log(1, 'indi_joystick_chg not yet implemented')

    def satellite_changed(self, name):
        if self.enable_satellite_changed:  # can be disabled during combobox update after new catalog selection
            self.st.selected_satellite = name
            age = self.st.t() - self.st.sat.epoch
            self.satLabel.setText('Valid elements, ' + '{:.2f} days old'.format(age))
            self.st.log(1, 'Satellite changed: ' + name)

    def tle_changed(self):
        self.st.set_tle(self.tleEdit.toPlainText())
        age = self.st.t() - self.st.sat.epoch
        self.satLabel.setText('Valid elements, ' + '{:.2f} days old'.format(age))
        self.st.log(1, 'Satellite changed')

    def location_changed(self):
        try:
            self.st.observer_alt = self.altitudeSpinBox.value()
            self.st.observer_lat = self.latitudeEdit.text()
            self.st.observer_lon = self.longitudeEdit.text()
            self.locationLabel.setText("Valid location")
        except ValueError as err:
            self.locationLabel.setText("Invalid location:\n" + err.args[0])

    def trackmode_changed(self, mode):
        self.st.log(1, 'trackmode_changed not yet implemented')

    def trackparam_changed(self, dummy):
        self.st.log(1, 'trackparam_changed not yet implemented')

    # System callbacks
    def connected(self):
        """ when INDI connection is established"""
        self.connectButton.setText("Disconnect")
        self.indiLabel.setText("Connected but driver not configured")
        self.telescopeComboBox.setEnabled(True)
        self.telescopeLabel_2.setEnabled(True)
        self.joystickLabel_2.setEnabled(True)
        self.hostEdit.setEnabled(False)
        self.portEdit.setEnabled(False)

    def disconnected(self):
        """ when INDI connection is ended"""
        self.telescopeComboBox.blockSignals(True)
        self.joystickCheckBox.blockSignals(True)

        self.connectButton.setText("Connect")
        self.indiLabel.setText("Not connected")
        self.telescopeComboBox.clear()
        self.telescopeComboBox.addItem("")
        self.telescopeComboBox.setEnabled(False)
        self.joystickCheckBox.setEnabled(False)
        self.telescopeLabel_2.setEnabled(False)
        self.joystickLabel_2.setEnabled(False)
        self.joystickCheckBox.setChecked(False)
        self.hostEdit.setEnabled(True)
        self.portEdit.setEnabled(True)

        self.joystickCheckBox.blockSignals(False)
        self.telescopeComboBox.blockSignals(False)

    def tracking_started(self):
        self.trackButton.setText("Stop tracking")

    def tracking_stopped(self):
        self.trackButton.setText("Track")

    def add_telescope(self, device_name):
        """ when INDI driver is detected"""
        self.telescopeComboBox.addItem(device_name)


    def add_joystick(self):
        self.joystickCheckBox.blockSignals(True)
        self.joystickCheckBox.setEnabled(True)
        self.joystickCheckBox.setChecked(True)
        self.joystickCheckBox.blockSignals(False)

    def update_sat_list(self):
        """ when satellite list shall be updated"""

        # build & sort key list
        keys = []
        selected_satellite_idx = -1
        for key in self.st.satellites_tle:
            keys.append(str(key))
        keys.sort()

        # update the combobox items, also memorise the index of selected satellite
        self.enable_satellite_changed = False
        self.satComboBox.clear()
        i = 0
        for key in keys:
            self.satComboBox.addItem(str(key))
            if key == self.st.selected_satellite:
                selected_satellite_idx = i
            i = i + 1
        self.enable_satellite_changed = True

        # define current item, modify the selected satellite if it has been remove from the list
        if selected_satellite_idx >= 0:
            self.satComboBox.setCurrentIndex(selected_satellite_idx)
        else:
            self.satComboBox.setCurrentIndex(0)
            self.satellite_changed(keys[0])

    # Update information panel every second time, sat location telescope location...)
    def timerEvent(self, event):
        # TODO: update when new number received instead of polling

        # Time
        self.timeLabel.setText(self.st.t_iso())

        # Satellite
        sat_ra, sat_dec, sat_distance = self.st.sat_pos()
        self.satRaLabel.setText(sat_ra.hstr())
        self.satDecLabel.setText(sat_dec.dstr())
        # TODO
        #self.satAltLabel.setText(sat_alt.dstr())
        #self.satAzLabel.setText(sat_az.dstr())
        self.satDistLabel.setText("{0:8.0f}km".format(sat_distance.km))
        #self.satShadowLabel.setText("N/A")

        # Telescope
        try:
            tel_ra, tel_dec = self.st.telescope_pos()
        except Error:
            self.telRaLabel.setText("-")
            self.telDecLabel.setText("-")
            #self.telAltLabel.setText("-")
            self.telAzLabel.setText("-")
        else:
            self.telRaLabel.setText(tel_ra.hstr())
            self.telDecLabel.setText(tel_dec.dstr())
            self.telAltLabel.setText("-")#TODO
            self.telAzLabel.setText("-")#TODO





class Timedialog(QtWidgets.QDialog, Ui_Timedialog):
    """ Dialog to set simulation time """

    def __init__(self, st):
        super(Timedialog, self).__init__()
        self.st = st

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


class Catalogdialog(QtWidgets.QDialog, Ui_Catalogdialog):
    """ Dialog to set satellite catalog """

    def __init__(self, st):
        super(Catalogdialog, self).__init__()
        self.st = st

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
        i = 0
        for catalog in self.st.catalogs:
            if self.listWidget.item(i).checkState() == QtCore.Qt.Checked:
                catalog.active = True
            else:
                catalog.active = False
            i = i + 1
        self.st.update_tle()

    def show_modal(self):
        self.setModal(True)
        self.show()
