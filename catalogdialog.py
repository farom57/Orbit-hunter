# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'catalogdialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Catalogdialog(object):
    def setupUi(self, Catalogdialog):
        Catalogdialog.setObjectName("Catalogdialog")
        Catalogdialog.resize(376, 292)
        self.verticalLayout = QtWidgets.QVBoxLayout(Catalogdialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Catalogdialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.listWidget = QtWidgets.QListWidget(Catalogdialog)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Catalogdialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Catalogdialog)
        self.buttonBox.accepted.connect(Catalogdialog.accept)
        self.buttonBox.rejected.connect(Catalogdialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Catalogdialog)

    def retranslateUi(self, Catalogdialog):
        _translate = QtCore.QCoreApplication.translate
        Catalogdialog.setWindowTitle(_translate("Catalogdialog", "Catalog selection"))
        self.label.setText(_translate("Catalogdialog", "Select active catalogs:"))

