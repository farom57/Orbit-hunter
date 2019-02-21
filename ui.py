"""
Author: Romain Fafet (farom57@gmail.com)
"""

from sattrack import *
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindow import Ui_MainWindow
from threading import Timer
import sys

class UI(QtWidgets.QMainWindow,  Ui_MainWindow):
    """ User interface of pySatTrack """

    def __init__(self,st):
        super(UI, self).__init__()
        self.st = st
        self.st.setUI(self)


        self.setupUi(self)




        # timer to update the time:
        self.timer=Timer(1., self.update_time)
        self.timer.start()



# Buttons

    def indi_connect_cmd(self):
        if self.st.is_connected():
            self.st.disconnect()
        else:
            self.st.connect()

    def indi_telescope_cfg_cmd(self):
        showinfo('Titre', 'indi_telescope_cfg_cmd not yet implemented')
    def indi_joystick_cfg_cmd(self):
        showinfo('Titre', 'indi_joystick_cfg_cmd not yet implemented')
    def sat_list_cat_cmd(self):
        showinfo('Titre', 'sat_list_cat_cmd not yet implemented')
    def track_btn_cmd(self):
        showinfo('Titre', 'track_btn_cmd not yet implemented')

# Values entered callbacks
    def sat_changed(self, text):
        self.sat_TLE_txt.delete('1.0', 'end')
        self.st.selected_satellite = self.sat_list.get()
        self.sat_TLE_txt.insert('1.0', self.st.selected_satellite + ' is selected')



    def location_changed(self):
        #try:
        self.st.observer_alt = self.obs_alt_var.get()
        self.st.observer_lat = self.obs_lat_var.get()
        self.st.observer_lon = self.obs_lon_var.get()
        #    self.obs_loc_str.set("Valid location")
        #except ValueError:
        #    self.obs_loc_str.set("Invalid location")
        return True

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
        self.obs_time_t_str.set("Time: "+self.st.t_iso())
        self.timer=Timer(1., self.update_time)
        self.timer.start()


