import logging
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDesktopWidget
from PyQt5 import QtWidgets
from iota import Address
import json

from messengerapp.db import mdatabase
from messengerapp.db.mdatabase import DBManager
from messengerapp.ui import mloginwidget, mchatwidget  # These files contain all of our UI designs
from messengerapp.iotacore.iotawrapper import IOTAWrapper
from messengerapp.utils.exceptions import AppException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

seed = "9MKUUMIQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLRUJOJC9QEXWCIL9HOUUWMDCAWGFAFSJM"
validated_seed = False
iota_wrapper = None

db_manager = DBManager()
db_account = None


class ChatWindow(QWidget, mchatwidget.Ui_Form):

    def __init__(self, parent=None):
        """ Showing a simple chat window with user's contacts and current/previous chat messages """
        super(ChatWindow, self).__init__(parent)
        self.setupUi(self)
        if db_account is not None:
            self.labelAccountName.setText(db_account.name)


class LoginWindow(QWidget, mloginwidget.Ui_Form):

    def __init__(self, parent=None):
        """ For user to input her seed. The seed is used to log into tangle net and access her local database
        which stores her contact and addresses """
        # require to have sup-class access to variables and methods from ui design:
        super(LoginWindow, self).__init__(parent)
        # setup the layout and widgets as defined in mdesign.py
        self.setupUi(self)
        # self.textEditSeed.returnPressed.connect(lambda: self.login_ok(True))
        self.textEditSeed.textChanged.connect(self.validate_seed)
        self.checkBoxVisibleSeed.stateChanged.connect(self.show_seed)
        # self.buttonLogin.accepted.connect(lambda: self.login_ok(True))
        self.buttonLogin.rejected.connect(lambda: self.close)
        global validated_seed
        validated_seed = False
        pass

    def show_seed(self):
        if self.checkBoxVisibleSeed.isChecked():
            self.textEditSeed.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.textEditSeed.setEchoMode(QtWidgets.QLineEdit.Password)

    def validate_seed(self):
        # Check the seed
        global validated_seed
        validated_seed = False
        global seed
        raw_seed = self.textEditSeed.text().__str__()
        try:
            checksum = IOTAWrapper.validate_seed(raw_seed)
            self.labelSeedShorten.setText("<font color='green'>{}</font>".format(checksum))
            validated_seed = True
            seed = raw_seed
        except AppException as e:
            self.labelSeedShorten.setText(e.feedback["message"])
            logger.exception(e)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(0, 0, 650, 550)
        self.center_on_screen()
        self.mLoginWindow, self.mChatWindow = None, None
        self.start_login_window()

    def start_login_window(self):
        """Create the Login Widget and attach it to our main window"""
        self.mLoginWindow = LoginWindow(self)
        self.setWindowTitle("Login")
        self.setCentralWidget(self.mLoginWindow)
        # Resize the window to widget size
        self.setFixedSize(self.mLoginWindow.size())
        # Set the button to open our chat messenger window
        self.mLoginWindow.buttonLogin.accepted.connect(self.start_chat_window)
        self.mLoginWindow.buttonLogin.rejected.connect(QApplication.exit)

    def start_chat_window(self):
        """ Create the Chat Widget and attach it to our main window"""
        self.mChatWindow = ChatWindow(self)
        self.setWindowTitle("Messenger")
        self.setCentralWidget(self.mChatWindow)
        # Resize the window to widget size
        self.setFixedSize(self.mChatWindow.size())
        init_account_with_seed()

    def center_on_screen(self):
        """ Centers the window on the screen. """
        # geometry of the main window
        qfr = self.frameGeometry()
        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        qfr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qfr.topLeft())


def init_account_with_seed():
    try:
        logger.info("Get Acc for seed: {}".format(seed))
        global db_account
        db_account = db_manager.search_account(seed)

        # TODO
        create_new_account("benuha")
    except:
        logger.exception("Cannot search db for account with seed: {}".format(seed))
    return None


def create_new_account(acc_name):
    """ Connect to tangle and request a new address for the current seed """
    try:
        global iota_wrapper
        iota_wrapper = IOTAWrapper(seed)
        response = iota_wrapper.create_new_address()
        m_address = Address(response, balance=response.balance, key_index=response.key_index,
                            security_level=response.security_level)

        private_key_b64, public_key_b64 = iota_wrapper.generate_rsa_key_pair()
        acc_address = mdatabase.Address(acc_name, m_address.address, m_address.key_index,
                                        public_key_b64, private_key_b64,
                                        m_address.checksum, m_address.balance)
        db_manager.add_account(seed, acc_address)
        # Public the public key of this account to tangle, so other can filter using tag
        message = {
            "name": acc_name,
            "public_key": public_key_b64.decode()  # decode to string
        }
        m_tag = iota_wrapper.get_tags(m_address.address[:27])

        logger.info("Address: {}".format(m_address.address))
        logger.info("TAG: {}".format(m_tag))
        logger.info("Message: {}".format(iota_wrapper.convert_string_to_trytes(json.dumps(message))))
        transfer = iota_wrapper.create_new_transaction(
            address=m_address.address,
            message=json.dumps(message),
            tag=m_tag
        )
        iota_wrapper.send_transaction(transfer)

    except:
        logger.exception("Failed to create new account using seed: {}".format(seed))
    pass


def run():
    # Create a new instance of QApplication
    app = QApplication(sys.argv)
    # Set the form to be our design MainWindow
    form = MainWindow()
    form.show()

    # Execute the app and wait for interaction
    sys.exit(app.exec())


if __name__ == '__main__':
    # Start the gui
    run()
