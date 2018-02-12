# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mchatwidget.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1059, 589)
        self.textChatMessage = QtWidgets.QTextEdit(Form)
        self.textChatMessage.setGeometry(QtCore.QRect(270, 499, 661, 61))
        self.textChatMessage.setObjectName("textChatMessage")
        self.labelAccountName = QtWidgets.QLabel(Form)
        self.labelAccountName.setGeometry(QtCore.QRect(10, 9, 391, 41))
        self.labelAccountName.setObjectName("labelAccountName")
        self.listAccounts = QtWidgets.QListView(Form)
        self.listAccounts.setGeometry(QtCore.QRect(10, 59, 256, 501))
        self.listAccounts.setObjectName("listAccounts")
        self.buttonSend = QtWidgets.QPushButton(Form)
        self.buttonSend.setGeometry(QtCore.QRect(950, 505, 99, 51))
        self.buttonSend.setObjectName("buttonSend")
        self.listMessages = QtWidgets.QListView(Form)
        self.listMessages.setGeometry(QtCore.QRect(270, 60, 781, 431))
        self.listMessages.setObjectName("listMessages")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.labelAccountName.setText(_translate("Form", "Account Name"))
        self.buttonSend.setText(_translate("Form", "OK"))

