import logging
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDesktopWidget
from PyQt5 import QtWidgets

from messengerapp.ui import mloginwidget, mchatwidget  # These files contain all of our UI designs
from messengerapp.iotacore.iotawrapper import IOTAWrapper
from messengerapp.utils.exceptions import AppException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatWindow(QWidget, mchatwidget.Ui_Form):

    def __init__(self, parent=None):
        super(ChatWindow, self).__init__(parent)
        self.setupUi(self)


class LoginWindow(QWidget, mloginwidget.Ui_Form):

    def __init__(self, parent=None):
        # require to have sup-class access to variables and methods from ui design:
        super(LoginWindow, self).__init__(parent)
        # setup the layout and widgets as defined in mdesign.py
        self.setupUi(self)
        # self.textEditSeed.returnPressed.connect(lambda: self.login_ok(True))
        self.textEditSeed.textChanged.connect(self.validate_seed)
        self.checkBoxVisibleSeed.stateChanged.connect(self.show_seed)
        # self.buttonLogin.accepted.connect(lambda: self.login_ok(True))
        self.buttonLogin.rejected.connect(lambda: self.close)
        self.validated = False
        pass

    def show_seed(self):
        if self.checkBoxVisibleSeed.isChecked():
            self.textEditSeed.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.textEditSeed.setEchoMode(QtWidgets.QLineEdit.Password)

    def validate_seed(self):
        # Check the seed
        self.validated = False
        _raw_seed = self.textEditSeed.text().__str__()
        try:
            checksum = IOTAWrapper.validate_seed(_raw_seed)
            self.labelSeedShorten.setText("<font color='green'>{}</font>".format(checksum))
            self.validated = True
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
