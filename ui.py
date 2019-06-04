"""
Author: Romain Fafet (farom57@gmail.com)
"""

from PyQt5 import QtCore, QtWidgets

from catalogdialog import Ui_Catalogdialog
from joystickdialog import Ui_Joystickdialog
from mainwindow import Ui_MainWindow
from sattrack import Error, SatTrack
from timedialog import Ui_Timedialog
from tledialog import Ui_Tledialog


class UI(QtWidgets.QMainWindow, Ui_MainWindow):
    """ User interface of pySatTrack """

    def __init__(self, st):
        super(UI, self).__init__()
        self.st = st  # type: SatTrack
        self.st.set_ui(self)
        self.setupUi(self)

        # Other init
        self.indi_telescope_options = ["None"]

        # Load dynamic content
        self.host_edit.setText(self.st.indi_server_ip)
        self.port_edit.setValue(self.st.indi_port)
        self.indi_lbl.setText("Not connected")
        self.p_gain_spinbox.setValue(self.st.p_gain)
        self.max_speed_spinbox.setValue(self.st.max_speed)
        self.joystick_speed_spinbox.setValue(self.st.joystick_speed)
        self.speed_lbl.setText("{0:7.3f} deg/s".format(self.st.joystick_speed))
        self.latitude_edit.setText(self.st.observer_lat)
        self.longitude_edit.setText(self.st.observer_lon)
        self.altitude_spinbox.setValue(self.st.observer_alt)

        self.update_sat_list()

        self.current_pass = self.st.next_pass(self.st.t())
        self.update_pass()

        # Slot connect to internal functions
        self.host_edit.textChanged.connect(self.connection_info_changed)
        self.port_edit.valueChanged.connect(self.connection_info_changed)
        self.connect_btn.clicked.connect(self.connect_clicked)
        self.telescope_combobox.currentIndexChanged['QString'].connect(self.telescope_changed)

        self.p_gain_spinbox.valueChanged['double'].connect(self.trackparam_changed)
        self.max_speed_spinbox.valueChanged['double'].connect(self.trackparam_changed)
        self.joystick_speed_spinbox.valueChanged['double'].connect(self.trackparam_changed)
        self.joystick_btn.clicked.connect(self.joystickconfig_clicked)

        self.center_btn.clicked.connect(self.track_clicked)
        self.up_left_btn.pressed.connect(self.move_up_left)
        self.up_btn.pressed.connect(self.move_up)
        self.up_right_btn.pressed.connect(self.move_up_right)
        self.left_btn.pressed.connect(self.move_left)
        self.right_btn.pressed.connect(self.move_right)
        self.down_left_btn.pressed.connect(self.move_down_left)
        self.down_btn.pressed.connect(self.move_up)
        self.down_right_btn.pressed.connect(self.move_down_right)
        self.up_left_btn.released.connect(self.move_stop)
        self.up_btn.released.connect(self.move_stop)
        self.up_right_btn.released.connect(self.move_stop)
        self.left_btn.released.connect(self.move_stop)
        self.right_btn.released.connect(self.move_stop)
        self.down_left_btn.released.connect(self.move_stop)
        self.down_btn.released.connect(self.move_stop)
        self.down_right_btn.released.connect(self.move_stop)

        self.latitude_edit.textChanged.connect(self.location_changed)
        self.longitude_edit.textChanged.connect(self.location_changed)
        self.altitude_spinbox.valueChanged['int'].connect(self.location_changed)

        self.real_time_btn.toggled['bool'].connect(self.timemode_changed)
        self.set_time_btn.clicked.connect(self.settime_clicked)

        self.catalog_sat_btn.toggled['bool'].connect(self.satmode_changed)
        self.sat_combobox.currentIndexChanged['QString'].connect(self.satellite_changed)
        self.enable_satellite_changed = True
        self.catalog_config_btn.clicked.connect(self.catconfig_clicked)
        self.set_TLE_btn.clicked.connect(self.tleconfig_clicked)

        self.prev_pass_btn.clicked.connect(self.prevpass_clicked)
        self.next_pass_btn.clicked.connect(self.nextpass_clicked)
        self.goto_rise_btn.clicked.connect(self.gotorise_clicked)
        self.goto_meridian_btn.clicked.connect(self.gotomeridian_clicked)

        # Additional slot connection to grey out widget depending on optionbox
        self.real_time_btn.toggled['bool'].connect(self.set_time_btn.setDisabled)
        self.catalog_sat_btn.toggled['bool'].connect(self.sat_combobox.setEnabled)
        self.catalog_sat_btn.toggled['bool'].connect(self.catalog_config_btn.setEnabled)
        self.catalog_sat_btn.toggled['bool'].connect(self.set_TLE_btn.setDisabled)
        # self.catalog_sat_btn.toggled['bool'].connect(self.tleEdit.setDisabled)

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

    def tleconfig_clicked(self):
        self.tledg = Tledialog(self)
        self.tledg.show_modal()

    def joystickconfig_clicked(self):
        self.joydg = Joystickdialog(self.st)
        self.joydg.show_modal()

    def nextpass_clicked(self):
        if self.current_pass[0][3] is not None:
            starting = self.current_pass[0][3]  # set date of the current pass
        else:
            starting = self.st.ts.tt(jd=self.current_pass[0][5] + 1)  # +24h if no current pass
        self.current_pass = self.st.next_pass(starting, backward=False)
        self.update_pass()

    def prevpass_clicked(self):
        if self.current_pass[0][0] is not None:
            starting = self.current_pass[0][0]  # rise date of the current pass
        else:
            starting = self.st.ts.tt(jd=self.current_pass[0][5] - 1)  # -24h if no current pass
        self.current_pass = self.st.next_pass(starting, backward=True)
        self.update_pass()

    def gotorise_clicked(self):
        self.st.log(1, 'gotorise not yet implemented')

    def gotomeridian_clicked(self):
        self.st.log(1, 'gotomeridian not yet implemented')

    # joystick btn
    def move_up_left(self):
        self.move_generic(1, 1)

    def move_up(self):
        self.move_generic(1, 0)

    def move_up_right(self):
        self.move_generic(1, -1)

    def move_left(self):
        self.move_generic(0, 1)

    def move_stop(self):
        self.move_generic(0, 0)

    def move_right(self):
        self.move_generic(0, -1)

    def move_down_left(self):
        self.move_generic(-1, 1)

    def move_down(self):
        self.move_generic(-1, 0)

    def move_down_right(self):
        self.move_generic(-1, -1)

    def move_generic(self, up_down, left_right):
        # move(1,1) for up & left, move(0,0) to stop, move(0,-1) for right, ...
        # TODO: mapping for ui buttons
        self.st.update_ui_offset(up_down, left_right, 0, 0, 0)

    # Values entered callbacks
    def connection_info_changed(self):
        self.st.indi_server_ip = self.host_edit.text()
        self.st.indi_port = self.port_edit.value()

    def timemode_changed(self, realtime):
        if realtime:
            self.st.observer_offset = 0

    def satmode_changed(self, catalog):
        if self.tle_sat_btn.isChecked():
            self.sat_lbl.setText('')

    def telescope_changed(self, driver):
        self.st.indiclient.set_telescope(driver)

    def satellite_changed(self, name):
        if self.enable_satellite_changed:  # can be disabled during combobox update after new catalog selection
            self.st.selected_satellite = name
            age = self.st.t() - self.st.sat.epoch
            self.sat_lbl.setText('Valid elements, ' + '{:.2f} days old'.format(age))
            self.st.log(1, 'Satellite changed: ' + name)
            self.current_pass = self.st.next_pass(self.st.t())
            self.update_pass()


    def location_changed(self):
        try:
            self.st.observer_alt = self.altitude_spinbox.value()
            self.st.observer_lat = self.latitude_edit.text()
            self.st.observer_lon = self.longitude_edit.text()
            self.location_lbl.setText("Valid location")
        except ValueError as err:
            self.location_lbl.setText("Invalid location:\n" + err.args[0])

    def trackmode_changed(self, mode):
        self.st.log(1, 'trackmode_changed not yet implemented')

    def trackparam_changed(self, dummy):
        self.st.log(1, 'trackparam_changed not yet implemented')

    # System callbacks
    def connected(self):
        """ when INDI connection is established"""
        self.connect_btn.setText("Disconnect")
        self.indi_lbl.setText("Connected but driver not configured")
        self.telescope_combobox.setEnabled(True)
        self.telescope_lbl.setEnabled(True)
        self.joystick_lbl.setEnabled(True)
        self.host_edit.setEnabled(False)
        self.port_edit.setEnabled(False)

    def disconnected(self):
        """ when INDI connection is ended"""
        self.telescope_combobox.blockSignals(True)
        self.joystick_btn.blockSignals(True)

        self.connect_btn.setText("Connect")
        self.indi_lbl.setText("Not connected")
        self.joystick_btn.setText("No joystick detected")
        self.telescope_combobox.clear()
        self.telescope_combobox.addItem("")
        self.telescope_combobox.setEnabled(False)
        self.joystick_btn.setEnabled(False)
        self.telescope_lbl.setEnabled(False)
        self.joystick_lbl.setEnabled(False)
        self.joystick_btn.setChecked(False)
        self.host_edit.setEnabled(True)
        self.port_edit.setEnabled(True)

        self.joystick_btn.blockSignals(False)
        self.telescope_combobox.blockSignals(False)

    def tracking_started(self):
        self.center_btn.setText("Stop tracking")

    def tracking_stopped(self):
        self.center_btn.setText("Track")

    def add_telescope(self, device_name):
        """ when INDI driver is detected"""
        self.telescope_combobox.addItem(device_name)

    def add_joystick(self):
        self.joystick_btn.blockSignals(True)
        self.joystick_btn.setEnabled(True)
        self.joystick_btn.setChecked(True)
        self.joystick_btn.setText("Configure")
        self.joystick_btn.blockSignals(False)

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
        self.sat_combobox.clear()
        i = 0
        for key in keys:
            self.sat_combobox.addItem(str(key))
            if key == self.st.selected_satellite:
                selected_satellite_idx = i
            i = i + 1
        self.enable_satellite_changed = True

        # define current item, modify the selected satellite if it has been remove from the list
        if selected_satellite_idx >= 0:
            self.sat_combobox.setCurrentIndex(selected_satellite_idx)
        else:
            self.sat_combobox.setCurrentIndex(0)
            self.satellite_changed(keys[0])

    def update_pass(self):
        if (self.current_pass[0][0] is not None):
            self.rise_time_lbl.setText(self.current_pass[0][0].utc_iso())
            self.rise_az_lbl.setText(str(self.current_pass[2][0]))
        else:
            self.rise_time_lbl.setText("-")
            self.rise_az_lbl.setText("-")

        if (self.current_pass[0][1] is not None):
            self.culmination_time_lbl.setText(self.current_pass[0][1].utc_iso())
            self.culmination_alt_lbl.setText(str(self.current_pass[1][1]))
            self.culmination_az_lbl.setText(str(self.current_pass[2][1]))
        else:
            self.culmination_time_lbl.setText("-")
            self.culmination_alt_lbl.setText("-")
            self.culmination_az_lbl.setText("-")

        if (self.current_pass[0][2] is not None):
            self.meridian_time_lbl.setText(self.current_pass[0][2].utc_iso())
            self.meridian_alt_lbl.setText(str(self.current_pass[1][2]))
            self.meridian_az_lbl.setText(str(self.current_pass[2][2]))
        else:
            self.meridian_time_lbl.setText("-")
            self.meridian_alt_lbl.setText("-")
            self.meridian_az_lbl.setText("-")

        if (self.current_pass[0][3] is not None):
            self.set_time_lbl.setText(self.current_pass[0][3].utc_iso())
            self.set_az_lbl.setText(str(self.current_pass[2][3]))
        else:
            self.set_time_lbl.setText("-")
            self.set_az_lbl.setText("-")

    # Update information panel every second time, sat location telescope location...)
    def timerEvent(self, event):

        # Time
        self.time_lbl.setText(self.st.t_iso())

        # Satellite
        sat_ra, sat_dec, sat_distance = self.st.sat_pos()
        sat_alt, sat_az = self.st.radec2altaz_2(sat_ra, sat_dec)
        self.sat_ra_lbl.setText(sat_ra.hstr())
        self.sat_dec_lbl.setText(sat_dec.dstr())
        self.sat_alt_lbl.setText(sat_alt.dstr())
        self.sat_az_lbl.setText(sat_az.dstr())
        self.sat_dist_lbl.setText("{0:8.0f}km".format(sat_distance.km))
        self.sat_shadow_lbl.setText(str(self.st.in_shadow()))

        # Telescope
        try:
            tel_ra, tel_dec = self.st.telescope_pos()
            tel_alt, tel_az = self.st.radec2altaz_2(tel_ra, tel_dec)
        except Error:
            self.tel_ra_lbl.setText("-")
            self.tel_dec_lbl.setText("-")
            self.tel_alt_lbl.setText("-")
            self.tel_az_lbl.setText("-")
        else:
            self.tel_ra_lbl.setText(tel_ra.hstr())
            self.tel_dec_lbl.setText(tel_dec.dstr())
            self.tel_alt_lbl.setText(tel_alt.dstr())
            self.tel_az_lbl.setText(tel_az.dstr())


class Timedialog(QtWidgets.QDialog, Ui_Timedialog):
    """ Dialog to set simulation time """

    def __init__(self, st):
        super(Timedialog, self).__init__()
        self.st = st

        # UI setup
        self.setupUi(self)
        self.buttonbox.accepted.connect(self.settime)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

        # set initial date to now
        datetime = QtCore.QDateTime.fromString(self.st.t_iso(), "yyyy-MM-ddTHH:mm:ssZ")
        datetime.setOffsetFromUtc(0)
        self.dateTime_edit.setDateTime(datetime)

    def settime(self):
        """ Called when OK button pressed """
        self.st.set_time(
            self.dateTime_edit.date().year(),
            self.dateTime_edit.date().month(),
            self.dateTime_edit.date().day(),
            self.dateTime_edit.time().hour(),
            self.dateTime_edit.time().minute(),
            self.dateTime_edit.time().second())

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
        self.buttonbox.accepted.connect(self.setcatalog)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

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


class Joystickdialog(QtWidgets.QDialog, Ui_Joystickdialog):
    """ Joystick configuration dialog """

    def __init__(self, st):
        super(Joystickdialog, self).__init__()
        self.st = st
        self.joystick_axes_n = self.st.indiclient.joystick_axes.nnp
        self.st.indiclient.joystick_conf_ui = self

        # UI setup
        self.setupUi(self, self.joystick_axes_n)

        self.buttonbox.accepted.connect(self.save_config)

        # load config
        if self.st.joystick_mapping is not None and len(self.st.joystick_mapping) == self.joystick_axes_n:
            config = self.st.joystick_mapping
            for i in range(self.joystick_axes_n):
                self.mapping_combo[i].setCurrentIndex(config[i][0])
                self.inverted_btn[i].setChecked(config[i][1])
        self.deadband_spinbox.setValue(self.st.joystick_deadband)
        self.expo_spinbox.setValue(self.st.joystick_expo)

    def done(self, res):
        self.killTimer(self.timer)
        super(Joystickdialog, self).done(res)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        for i in range(self.joystick_axes_n):
            self.progressBar[i].setValue(int(self.st.indiclient.joystick_axes[i].value))

    def show_modal(self):
        self.setModal(True)
        self.show()

        # timer to update the input values:
        self.timer = self.startTimer(40)

    def save_config(self):
        config = []
        for i in range(self.joystick_axes_n):
            config.append((self.mapping_combo[i].currentIndex(), self.inverted_btn[i].isChecked()))

        self.st.joystick_mapping = config
        self.st.joystick_deadband = self.deadband_spinbox.value()
        self.st.joystick_expo = self.expo_spinbox.value()


class Tledialog(QtWidgets.QDialog, Ui_Tledialog):
    """ Dialog to set TLE """
    trigger = QtCore.pyqtSignal()

    def __init__(self, ui):
        super(Tledialog, self).__init__()
        self.ui = ui
        self.st = ui.st

        # UI setup
        self.setupUi(self)

        self.button_box.accepted.connect(self.set_tle)

    def set_tle(self):
        """ Update catalog checked states """
        try:
            self.st.set_tle(self.tle_edit.toPlainText())
            age = self.st.t() - self.st.sat.epoch
            self.ui.sat_lbl.setText('Valid elements, ' + '{:.2f} days old'.format(age))
            self.trigger.connect(self.accept)
            self.trigger.emit()
        except ValueError as err:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid TLE: {0}".format(err), QtWidgets.QMessageBox.Close)

    def show_modal(self):
        self.setModal(True)
        self.show()
