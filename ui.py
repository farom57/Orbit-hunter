"""
Author: Romain Fafet (farom57@gmail.com)
"""

from configuration import *
from tracker import *

from tkinter import *
from tkinter.ttk import *

class UI(object):
    """ User interface of pySatTrack

    The UI modifies the Configuration (conf) and control the Tracker to start
    and stop.
    The user interface is based on Tkinter

    """

    def __init__(self, tracker):
        self.tracker = tracker
        self.conf = self.tracker.conf
        self.tracker.register_ui(self)

        self.main_frame = Tk()
        '''self.indi_status_label = Label(self.main_frame,  text="Not connected")
        self.indi_status_label.pack()
        print("test")'''

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
        self.indi_connect = Button(self.indi_frame, textvariable=self.indi_connect_var)

        self.indi_telescope_row = Frame(self.indi_frame)
        self.indi_telescope_lbl = Label(self.indi_telescope_row,  text="Telescope:")
        self.indi_telescope_options = ("None", )
        self.indi_telescope_var = StringVar()
        self.indi_telescope_var.set(self.indi_telescope_options[0])
        self.indi_telescope = OptionMenu(self.indi_telescope_row, self.indi_telescope_var, *self.indi_telescope_options)
        self.indi_telescope .config(width = 12)
        self.indi_telescope_cfg = Button(self.indi_telescope_row, text="Config",  width = 6)

        self.indi_joystick_row = Frame(self.indi_frame)
        self.indi_joystick_lbl = Label(self.indi_joystick_row,  text="Joystick:")
        self.indi_joystick_options = ("None",)
        self.indi_joystick_var = StringVar()
        self.indi_joystick_var.set(self.indi_joystick_options[0])
        self.indi_joystick = OptionMenu(self.indi_joystick_row, self.indi_joystick_var, *self.indi_joystick_options)
        self.indi_joystick.config(width = 12)
        self.indi_joystick_cfg = Button(self.indi_joystick_row, text="Config",  width = 6)

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

        self.main_frame.mainloop()










