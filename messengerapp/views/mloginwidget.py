# -*- coding: utf-8 -*-

# Form implementation generated from reading views file 'mloginwidget.views'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(593, 171)
        Form.setAutoFillBackground(True)
        self.labelInsertSeed = QtWidgets.QLabel(Form)
        self.labelInsertSeed.setGeometry(QtCore.QRect(14, 10, 491, 31))
        self.labelInsertSeed.setMaximumSize(QtCore.QSize(16777215, 109))
        self.labelInsertSeed.setObjectName("labelInsertSeed")
        self.buttonLogin = QtWidgets.QDialogButtonBox(Form)
        self.buttonLogin.setGeometry(QtCore.QRect(10, 130, 176, 27))
        self.buttonLogin.setMaximumSize(QtCore.QSize(176, 16777215))
        self.buttonLogin.setStandardButtons(QtWidgets.QDialogButtonBox.Close|QtWidgets.QDialogButtonBox.Ok)
        self.buttonLogin.setObjectName("buttonLogin")
        self.textEditSeed = QtWidgets.QLineEdit(Form)
        self.textEditSeed.setGeometry(QtCore.QRect(10, 40, 571, 31))
        self.textEditSeed.setAutoFillBackground(False)
        self.textEditSeed.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.textEditSeed.setText("")
        self.textEditSeed.setEchoMode(QtWidgets.QLineEdit.Password)
        self.textEditSeed.setClearButtonEnabled(True)
        self.textEditSeed.setObjectName("textEditSeed")
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 80, 571, 41))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelSeedShorten = QtWidgets.QLabel(self.layoutWidget)
        self.labelSeedShorten.setText("")
        self.labelSeedShorten.setObjectName("labelSeedShorten")
        self.horizontalLayout.addWidget(self.labelSeedShorten)
        self.checkBoxVisibleSeed = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBoxVisibleSeed.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBoxVisibleSeed.sizePolicy().hasHeightForWidth())
        self.checkBoxVisibleSeed.setSizePolicy(sizePolicy)
        self.checkBoxVisibleSeed.setMaximumSize(QtCore.QSize(70, 22))
        self.checkBoxVisibleSeed.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.checkBoxVisibleSeed.setAutoFillBackground(False)
        self.checkBoxVisibleSeed.setObjectName("checkBoxVisibleSeed")
        self.horizontalLayout.addWidget(self.checkBoxVisibleSeed)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.labelInsertSeed.setText(_translate("Form", "Insert your seed here"))
        self.textEditSeed.setToolTip(_translate("Form", "<html><head/><body><p>your personal iota wallet seed</p></body></html>"))
        self.labelSeedShorten.setToolTip(_translate("Form", "<html><head/><body><p>Seed checksum</p></body></html>"))
        self.labelSeedShorten.setWhatsThis(_translate("Form", "<html><head/><body><p>Seed checksum</p></body></html>"))
        self.checkBoxVisibleSeed.setText(_translate("Form", "Visible"))

