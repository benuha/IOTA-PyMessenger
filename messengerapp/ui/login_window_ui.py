import logging
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor

from messengerapp.views import mloginwidget
from messengerapp.iotacore.iotawrapper import IOTAWrapper
from messengerapp.utils.exceptions import AppException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoginWindow(QWidget, mloginwidget.Ui_Form):

    def __init__(self, parent=None, fn_login_account_with_seed=None):
        """ For user to input her seed. The seed is used to log into tangle net and access her local database
        which stores her contact and addresses """
        # require to have sup-class access to variables and methods from views design:
        super(LoginWindow, self).__init__(parent)
        # setup the layout and widgets as defined in mloginwidget.py
        self.setupUi(self)

        self.is_validated_seed = False
        self.fn_login_account_with_seed = fn_login_account_with_seed
        self.textEditSeed.textChanged.connect(
            self.validate_seed
        )
        self.textEditSeed.returnPressed.connect(
            self.on_login_with_seed
        )

        # Set the button to open our chat messenger window
        self.buttonLogin.accepted.connect(
            self.on_login_with_seed
        )
        self.buttonLogin.rejected.connect(lambda: self.close)

        self.checkBoxVisibleSeed.stateChanged.connect(self.show_seed)
        # self.setAutoFillBackground(True)
        # p = self.palette()
        # p.setColor(self.backgroundRole(), QColor(92, 107, 192))
        # self.setPalette(p)

        self.textEditSeed.setFocus()
        self.hide()

    def on_login_with_seed(self):
        self.validate_seed()
        if self.is_validated_seed:
            self.fn_login_account_with_seed(self.textEditSeed.text().__str__(), self.parent())

    def show_seed(self):
        if self.checkBoxVisibleSeed.isChecked():
            self.textEditSeed.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.textEditSeed.setEchoMode(QtWidgets.QLineEdit.Password)

    def validate_seed(self):
        # Check the seed
        self.is_validated_seed = False
        raw_seed = self.textEditSeed.text().__str__()
        if raw_seed is None or len(raw_seed) < 81:
            self.labelSeedShorten.setText("<font color='red'>{}</font>".format("Invalid"))
            return

        try:
            checksum = IOTAWrapper.validate_seed(raw_seed)
            self.labelSeedShorten.setText("<font color='green'>{}</font>".format(checksum))
            self.is_validated_seed = True
        except AppException as e:
            self.labelSeedShorten.setText(e.feedback["message"])
            logger.exception(e)
