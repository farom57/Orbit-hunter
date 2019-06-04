# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tledialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Tledialog(object):
    def setupUi(self, Tledialog):
        Tledialog.setObjectName("Tledialog")
        Tledialog.resize(591, 156)
        self.verticalLayout = QtWidgets.QVBoxLayout(Tledialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Tledialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.tle_edit = QtWidgets.QPlainTextEdit(Tledialog)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Mono")
        self.tle_edit.setFont(font)
        self.tle_edit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.tle_edit.setObjectName("tle_edit")
        self.verticalLayout.addWidget(self.tle_edit)
        self.button_box = QtWidgets.QDialogButtonBox(Tledialog)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)

        self.retranslateUi(Tledialog)
        self.button_box.rejected.connect(Tledialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Tledialog)

    def retranslateUi(self, Tledialog):
        _translate = QtCore.QCoreApplication.translate
        Tledialog.setWindowTitle(_translate("Tledialog", "TLE"))
        self.label.setText(_translate("Tledialog", "Enter the TLE (lines 1 and 2 only):"))
        self.tle_edit.setPlainText(_translate("Tledialog", "1 NNNNNU NNNNNAAA NNNNN.NNNNNNNN +.NNNNNNNN +NNNNN-N +NNNNN-N N NNNNN\n"
"2 NNNNN NNN.NNNN NNN.NNNN NNNNNNN NNN.NNNN NNN.NNNN NN.NNNNNNNNNNNNNN"))


