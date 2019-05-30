from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Joystickdialog(object):
    def setupUi(self, Joystickdialog, n_axis):
        Joystickdialog.setObjectName("Joystickdialog")
        Joystickdialog.resize(563, 212)
        self.verticalLayout = QtWidgets.QVBoxLayout(Joystickdialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.axis_lbl = QtWidgets.QLabel(Joystickdialog)
        self.axis_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.axis_lbl.setObjectName("axis_lbl")
        self.gridLayout.addWidget(self.axis_lbl, 0, 0, 1, 1)
        self.value_lbl = QtWidgets.QLabel(Joystickdialog)
        self.value_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.value_lbl.setObjectName("value_lbl")
        self.gridLayout.addWidget(self.value_lbl, 0, 1, 1, 1)
        self.mapping_lbl = QtWidgets.QLabel(Joystickdialog)
        self.mapping_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.mapping_lbl.setObjectName("mapping_lbl")
        self.gridLayout.addWidget(self.mapping_lbl, 0, 2, 1, 1)
        self.invert_lbl = QtWidgets.QLabel(Joystickdialog)
        self.invert_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.invert_lbl.setObjectName("invert_lbl")
        self.gridLayout.addWidget(self.invert_lbl, 0, 3, 1, 1)

        self.axis_n_lbl = []
        self.progressBar = []
        self.mapping_combo = []
        self.inverted_btn = []

        for i in range(n_axis):
            self.axis_n_lbl.append(QtWidgets.QLabel(Joystickdialog))
            self.axis_n_lbl[i].setAlignment(QtCore.Qt.AlignCenter)
            self.axis_n_lbl[i].setObjectName("axis_n_lbl_"+str(i))
            self.axis_n_lbl[i].setText(str(i+1))
            self.gridLayout.addWidget(self.axis_n_lbl[i], i+1, 0, 1, 1)

            self.progressBar.append(QtWidgets.QProgressBar(Joystickdialog))
            self.progressBar[i].setMinimum(-32767)
            self.progressBar[i].setMaximum(32767)
            self.progressBar[i].setProperty("value", 0)
            self.progressBar[i].setObjectName("progressBar_"+str(i))
            self.progressBar[i].setFormat("%v")
            self.gridLayout.addWidget(self.progressBar[i], i+1, 1, 1, 1)

            self.mapping_combo.append(QtWidgets.QComboBox(Joystickdialog))
            self.mapping_combo[i].setMinimumSize(QtCore.QSize(130, 0))
            self.mapping_combo[i].setObjectName("mapping_combo_"+str(i))
            self.mapping_combo[i].addItem("None")
            self.mapping_combo[i].addItem("North / south")
            self.mapping_combo[i].addItem("East / west")
            self.mapping_combo[i].addItem("Front / back")
            self.mapping_combo[i].addItem("Left / right")
            self.mapping_combo[i].addItem("Timeshift")
            self.gridLayout.addWidget(self.mapping_combo[i], i+1, 2, 1, 1)

            self.inverted_btn.append(QtWidgets.QCheckBox(Joystickdialog))
            self.inverted_btn[i].setObjectName("inverted_btn_"+str(i))
            self.gridLayout.addWidget(self.inverted_btn[i], i+1, 3, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.deadBandLabel = QtWidgets.QLabel(Joystickdialog)
        self.deadBandLabel.setObjectName("deadBandLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.deadBandLabel)
        self.deadband_spinbox = QtWidgets.QSpinBox(Joystickdialog)
        self.deadband_spinbox.setToolTip("")
        self.deadband_spinbox.setMaximum(32766)
        self.deadband_spinbox.setSingleStep(100)
        self.deadband_spinbox.setProperty("value", 2000)
        self.deadband_spinbox.setObjectName("deadband_spinbox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.deadband_spinbox)
        self.expoLabel = QtWidgets.QLabel(Joystickdialog)
        self.expoLabel.setObjectName("expoLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.expoLabel)
        self.expo_spinbox = QtWidgets.QDoubleSpinBox(Joystickdialog)
        self.expo_spinbox.setToolTip("")
        self.expo_spinbox.setDecimals(1)
        self.expo_spinbox.setMaximum(1.0)
        self.expo_spinbox.setSingleStep(0.1)
        self.expo_spinbox.setObjectName("expo_spinbox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.expo_spinbox)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Joystickdialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Joystickdialog)
        self.buttonBox.accepted.connect(Joystickdialog.accept)
        self.buttonBox.rejected.connect(Joystickdialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Joystickdialog)

    def retranslateUi(self, Joystickdialog):
        _translate = QtCore.QCoreApplication.translate
        Joystickdialog.setWindowTitle(_translate("Joystickdialog", "Joystick configuration"))
        self.value_lbl.setText(_translate("Joystickdialog", "Value"))
        self.mapping_lbl.setText(_translate("Joystickdialog", "Mapping"))
        self.invert_lbl.setText(_translate("Joystickdialog", "Invert"))
        self.axis_lbl.setText(_translate("Joystickdialog", "Axis"))
        self.deadBandLabel.setText(_translate("Joystickdialog", "Dead-band:"))
        self.expoLabel.setText(_translate("Joystickdialog", "Expo:"))


