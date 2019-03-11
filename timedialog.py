# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timedialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Timedialog(object):
    def setupUi(self, Timedialog):
        Timedialog.setObjectName("Timedialog")
        Timedialog.resize(293, 107)
        self.verticalLayout = QtWidgets.QVBoxLayout(Timedialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Timedialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(Timedialog)
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-ddTHH:mm:ssZ")
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.verticalLayout.addWidget(self.dateTimeEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(Timedialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Timedialog)
        QtCore.QMetaObject.connectSlotsByName(Timedialog)

    def retranslateUi(self, Timedialog):
        _translate = QtCore.QCoreApplication.translate
        Timedialog.setWindowTitle(_translate("Timedialog", "Simulation time setting"))
        self.label.setText(_translate("Timedialog", "Simulation start date (UTC time zone):"))

