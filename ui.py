"""
Author: Romain Fafet (farom57@gmail.com)
"""

from sattrack import *

from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showinfo
from threading import Timer
import Pmw

class UI(object):
    """ User interface of pySatTrack

    The user interface is based on Tkinter

    """

    def __init__(self,st):
        self.st = st
        self.st.setUI(self)

        self.main_frame = Pmw.initialise()

# INDI
        self.indi_frame = LabelFrame(self.main_frame, text="INDI")

        self.indi_host_row = Frame(self.indi_frame)
        self.indi_host_var = StringVar()
        self.indi_host_var.set("localhost")
        self.indi_host = Entry(self.indi_host_row,  textvariable=self.indi_host_var)
        self.indi_host_lbl = Label(self.indi_host_row,  text="Host:")

        self.indi_port_row = Frame(self.indi_frame)
        self.indi_port_var = StringVar()
        self.indi_port_var.set("7624")
        self.indi_port = Entry(self.indi_port_row,  textvariable=self.indi_port_var)
        self.indi_port_lbl = Label(self.indi_port_row,  text="Port:")


        self.indi_connect_var = StringVar()
        self.indi_connect_var.set("Connect")
        self.indi_connect = Button(self.indi_frame, textvariable=self.indi_connect_var,  command=self.indi_connect_cmd)

        self.indi_telescope_row = Frame(self.indi_frame)
        self.indi_telescope_lbl = Label(self.indi_telescope_row,  text="Telescope:")
        self.indi_telescope_options = ["None", "None bis"]
        self.indi_telescope_var = StringVar()
        self.indi_telescope_var.set(self.indi_telescope_options[0])
        self.indi_telescope = OptionMenu(self.indi_telescope_row, self.indi_telescope_var, *self.indi_telescope_options)
        self.indi_telescope .config(width = 12)
        self.indi_telescope_cfg = Button(self.indi_telescope_row, text="Config",  width = 6, command=self.indi_telescope_cfg_cmd)

        self.indi_joystick_row = Frame(self.indi_frame)
        self.indi_joystick_lbl = Label(self.indi_joystick_row,  text="Joystick:")
        self.indi_joystick_options = ["None"]
        self.indi_joystick_var = StringVar()
        self.indi_joystick_var.set(self.indi_joystick_options[0])
        self.indi_joystick = OptionMenu(self.indi_joystick_row, self.indi_joystick_var, *self.indi_joystick_options)
        self.indi_joystick.config(width = 12)
        self.indi_joystick_cfg = Button(self.indi_joystick_row, text="Config",  width = 6, command=self.indi_joystick_cfg_cmd)

        self.indi_status_var = StringVar()
        self.indi_status_var.set("Not connected")
        self.indi_status_label = Label(self.indi_frame,  textvariable=self.indi_status_var)

        self.indi_frame.pack()
        self.indi_host_row.pack(fill=X)
        self.indi_host_lbl.pack(side=LEFT)
        self.indi_host.pack(side=RIGHT)
        self.indi_port_row.pack(fill=X)
        self.indi_port_lbl.pack(side=LEFT)
        self.indi_port.pack(side=RIGHT)
        self.indi_connect.pack(fill=X)
        self.indi_telescope_row.pack(fill=X)
        self.indi_telescope_lbl.pack(side=LEFT)
        self.indi_telescope_cfg.pack(side=RIGHT)
        self.indi_telescope.pack(side=RIGHT)
        self.indi_joystick_row.pack(fill=X)
        self.indi_joystick_lbl.pack(side=LEFT)
        self.indi_joystick_cfg.pack(side=RIGHT)
        self.indi_joystick.pack(side=RIGHT)
        self.indi_status_label.pack(fill=X)

# Satellite

        self.sat_frame = LabelFrame(self.main_frame, text="Satellite")

        self.sat_list_row = Frame(self.sat_frame)
        self.sat_list_lbl = Label(self.sat_list_row,  text="Satellite:")
        self.sat_list_options = list(self.st.satellites_tle.keys())
        '''self.sat_list_var = StringVar()
        self.sat_list_var.set(self.sat_list_options[0])
        self.sat_list = OptionMenu(self.sat_list_row, self.indi_joystick_var, *self.sat_list_options)'''
        self.sat_list = Pmw.ComboBox(self.sat_list_row,scrolledlist_items = self.sat_list_options,listheight = 150, history=0, selectioncommand = self.sat_changed)
        self.sat_list.config(width = 20)
        self.sat_list.selectitem(self.st.selected_satellite)
        self.sat_list_cat = Button(self.sat_list_row, text="Catalogs", width = 6, command=self.sat_list_cat_cmd)

        self.sat_TLE_lbl = Label(self.sat_frame,  text="TLE:")
        self.sat_TLE_txt = Text(self.sat_frame,  height=2,  width=69)

        self.sat_ephem_var = StringVar()
        self.sat_ephem_var.set("Please select a satellite or enter TLE")
        self.sat_ephem = Label(self.sat_frame, textvariable=self.sat_ephem_var, justify=LEFT)

        self.sat_frame.pack()
        self.sat_list_row.pack()
        self.sat_list_lbl.pack(side=LEFT)
        self.sat_list.pack(side=LEFT)
        self.sat_list_cat.pack(side=LEFT)
        self.sat_TLE_lbl.pack(fill=X)
        self.sat_TLE_txt.pack()
        self.sat_ephem.pack()

# Observer
        self.obs_frame = LabelFrame(self.main_frame, text="Observer")
        self.obs_loc_str = StringVar()

        self.obs_lat_row = Frame(self.obs_frame)
        self.obs_lat_label = Label(self.obs_lat_row, text="Latitude: ")
        self.obs_lat_var = StringVar()
        self.obs_lat_var.set(self.st.observer_lat)
        self.obs_lat = Entry(self.obs_lat_row,  textvariable=self.obs_lat_var, validate="focusout", validatecommand=self.location_changed)

        self.obs_lon_row = Frame(self.obs_frame)
        self.obs_lon_label =Label(self.obs_lon_row, text="Longitude: ")
        self.obs_lon_var = StringVar()
        self.obs_lon_var.set(self.st.observer_lon)
        self.obs_lon = Entry(self.obs_lon_row,  textvariable=self.obs_lon_var, validate="focusout", validatecommand=self.location_changed)

        self.obs_alt_row = Frame(self.obs_frame)
        self.obs_alt_label = Label(self.obs_alt_row, text="Altitude (m): ")
        self.obs_alt_var = DoubleVar()
        self.obs_alt_var.set(self.st.observer_alt)
        self.obs_alt = Spinbox(self.obs_alt_row, from_=0, to=10000, textvariable=self.obs_alt_var, validate="focusout", validatecommand=self.location_changed)

        self.obs_offset_row = Frame(self.obs_frame)
        self.obs_offset_label = Label(self.obs_offset_row, text="Time offset (min): ")
        self.obs_offset_var = DoubleVar()
        self.obs_offset_var.set(self.st.observer_offset)
        self.obs_offset = Spinbox(self.obs_offset_row,from_=-9999999, to=9999999, textvariable=self.obs_offset_var)

        #self.obs_loc_str = StringVar()
        self.obs_loc_str.set("Not initialized")
        self.obs_loc_lbl = Label(self.obs_frame, textvariable=self.obs_loc_str)

        self.obs_time_ts = load.timescale()
        self.obs_time_t = self.obs_time_ts.now()
        tmp=self.obs_time_ts.now().tt + self.obs_offset_var.get()/24/60
        self.obs_time_t = self.obs_time_ts.tt(jd=tmp)
        self.obs_time_t_str = StringVar()
        self.obs_time_t_str.set("Time: "+self.obs_time_t.utc_iso())
        self.obs_time_lbl = Label(self.obs_frame, textvariable=self.obs_time_t_str)

        self.obs_frame.pack()
        self.obs_lat_row.pack()
        self.obs_lat_label.pack(side=LEFT)
        self.obs_lat.pack(side=LEFT)
        self.obs_lon_row .pack()
        self.obs_lon_label.pack(side=LEFT)
        self.obs_lon.pack(side=LEFT)
        self.obs_alt_row.pack()
        self.obs_alt_label.pack(side=LEFT)
        self.obs_alt.pack(side=LEFT)
        self.obs_offset_row.pack()
        self.obs_offset_label.pack(side=LEFT)
        self.obs_offset.pack(side=LEFT)
        self.obs_loc_lbl.pack()
        self.obs_time_lbl.pack()

# Tracker
        self.track_frame = LabelFrame(self.main_frame, text="Tracking")

        self.track_method_row = Frame(self.track_frame)
        self.track_method_lbl = Label(self.track_method_row, text="Method:")
        self.track_method_options = ("Goto","Move","Timed move", "Speed")
        self.track_method_var = StringVar()
        self.track_method_var.set(self.st.track_method)
        self.track_method = OptionMenu(self.track_method_row, self.track_method_var, *self.track_method_options)

        self.track_P_row = Frame(self.track_frame)
        self.track_P_label = Label(self.track_P_row, text="P gain: ")
        self.track_P_var = DoubleVar()
        self.track_P_var.set(self.st.p_gain)
        self.track_P = Spinbox(self.track_P_row, from_=0, to=10, increment=0.1,  textvariable=self.track_P_var)

        self.track_I_row = Frame(self.track_frame)
        self.track_I_label = Label(self.track_I_row, text="Tau I: ")
        self.track_I_var = DoubleVar()
        self.track_I_var.set(self.st.tau_i)
        self.track_I = Spinbox(self.track_I_row, from_=0, to=100, increment=0.1,  textvariable=self.track_I_var)

        self.track_D_row = Frame(self.track_frame)
        self.track_D_label = Label(self.track_D_row, text="Tau D: ")
        self.track_D_var = DoubleVar()
        self.track_D_var.set(self.st.tau_d)
        self.track_D = Spinbox(self.track_D_row, from_=0, to=100, increment=0.1,  textvariable=self.track_D_var)

        self.track_maxrate_row = Frame(self.track_frame)
        self.track_maxrate_label = Label(self.track_maxrate_row, text="Max rate: ")
        self.track_maxrate_var = DoubleVar()
        self.track_maxrate_var.set(self.st.max_rate)
        self.track_maxrate = Spinbox(self.track_maxrate_row, from_=0, to=1000, increment=1,  textvariable=self.track_maxrate_var)

        self.track_isat_row = Frame(self.track_frame)
        self.track_isat_label = Label(self.track_isat_row, text="Saturation: ")
        self.track_isat_var = DoubleVar()
        self.track_isat_var.set(self.st.i_sat)
        self.track_isat = Spinbox(self.track_isat_row, from_=0, to=2, increment=0.1,  textvariable=self.track_isat_var)

        self.track_btn_txt = StringVar()
        self.track_btn_txt.set("Connect")
        self.track_btn = Button(self.track_frame, textvariable=self.track_btn_txt, command=self.track_btn_cmd)

        self.track_status_txt = StringVar()
        self.track_status_txt.set("Not connected")
        self.track_status_lbl = Label(self.track_frame, textvariable=self.track_status_txt)

        self.track_frame.pack()
        self.track_method_row.pack()
        self.track_method_lbl.pack(side=LEFT)
        self.track_method.pack(side=LEFT)
        self.track_P_row.pack()
        self.track_P_label.pack(side=LEFT)
        self.track_P.pack(side=LEFT)
        self.track_I_row.pack()
        self.track_I_label.pack(side=LEFT)
        self.track_I.pack(side=LEFT)
        self.track_D_row.pack()
        self.track_D_label.pack(side=LEFT)
        self.track_D.pack(side=LEFT)
        self.track_maxrate_row.pack()
        self.track_maxrate_label.pack(side=LEFT)
        self.track_maxrate.pack(side=LEFT)
        self.track_isat_row.pack()
        self.track_isat_label.pack(side=LEFT)
        self.track_isat.pack(side=LEFT)
        self.track_btn.pack()
        self.track_status_lbl.pack()


        # timer to update the time:
        self.timer=Timer(1., self.update_time)
        self.timer.start()
        self.location_changed()
        self.sat_changed('')


        self.main_frame.mainloop()


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


