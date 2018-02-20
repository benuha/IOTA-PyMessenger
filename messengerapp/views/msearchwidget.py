# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'msearchwidget.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(591, 125)
        Dialog.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.buttonsSearch = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonsSearch.setGeometry(QtCore.QRect(400, 80, 181, 32))
        self.buttonsSearch.setOrientation(QtCore.Qt.Horizontal)
        self.buttonsSearch.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonsSearch.setObjectName("buttonsSearch")
        self.labelDialog = QtWidgets.QLabel(Dialog)
        self.labelDialog.setGeometry(QtCore.QRect(10, 10, 571, 31))
        self.labelDialog.setObjectName("labelDialog")
        self.editAccSearch = QtWidgets.QLineEdit(Dialog)
        self.editAccSearch.setGeometry(QtCore.QRect(10, 40, 571, 31))
        self.editAccSearch.setClearButtonEnabled(True)
        self.editAccSearch.setObjectName("editAccSearch")
        self.labelStatus = QtWidgets.QLabel(Dialog)
        self.labelStatus.setGeometry(QtCore.QRect(10, 80, 381, 31))
        self.labelStatus.setText("")
        self.labelStatus.setObjectName("labelStatus")

        self.retranslateUi(Dialog)
        self.buttonsSearch.accepted.connect(Dialog.accept)
        self.buttonsSearch.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add Friend"))
        self.labelDialog.setText(_translate("Dialog", "Search Tangle for account"))

