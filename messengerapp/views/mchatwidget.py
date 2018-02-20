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
        Form.resize(1059, 604)
        Form.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.textChatMessage = QtWidgets.QTextEdit(Form)
        self.textChatMessage.setGeometry(QtCore.QRect(270, 509, 661, 51))
        self.textChatMessage.setObjectName("textChatMessage")
        self.labelAccName = QtWidgets.QLabel(Form)
        self.labelAccName.setGeometry(QtCore.QRect(70, 10, 981, 41))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(False)
        self.labelAccName.setFont(font)
        self.labelAccName.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.labelAccName.setObjectName("labelAccName")
        self.buttonSend = QtWidgets.QPushButton(Form)
        self.buttonSend.setGeometry(QtCore.QRect(950, 505, 99, 51))
        self.buttonSend.setObjectName("buttonSend")
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(10, 570, 251, 23))
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", -1)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.buttonAddFriend = QtWidgets.QPushButton(Form)
        self.buttonAddFriend.setGeometry(QtCore.QRect(27, 510, 231, 41))
        self.buttonAddFriend.setObjectName("buttonAddFriend")
        self.listContacts = QtWidgets.QListWidget(Form)
        self.listContacts.setGeometry(QtCore.QRect(10, 60, 256, 441))
        self.listContacts.setObjectName("listContacts")
        self.labelAccImage = QtWidgets.QLabel(Form)
        self.labelAccImage.setGeometry(QtCore.QRect(20, 10, 41, 41))
        self.labelAccImage.setAutoFillBackground(True)
        self.labelAccImage.setFrameShape(QtWidgets.QFrame.Box)
        self.labelAccImage.setText("")
        self.labelAccImage.setScaledContents(True)
        self.labelAccImage.setObjectName("labelAccImage")
        self.listMessages = QtWidgets.QListWidget(Form)
        self.listMessages.setGeometry(QtCore.QRect(275, 61, 771, 441))
        self.listMessages.setObjectName("listMessages")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.textChatMessage.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.textChatMessage.setPlaceholderText(_translate("Form", "Start your chat here"))
        self.labelAccName.setText(_translate("Form", "No Account specified"))
        self.buttonSend.setText(_translate("Form", "OK"))
        self.buttonAddFriend.setText(_translate("Form", "Add Contact"))

