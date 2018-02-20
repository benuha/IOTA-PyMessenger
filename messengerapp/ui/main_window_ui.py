from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication

from messengerapp.ui.chat_window_ui import ChatWindow
from messengerapp.ui.login_window_ui import LoginWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(0, 0, 650, 550)
        self.center_on_screen()
        self.mLoginWindow, self.mChatWindow = None, None

    def start_login_window(self):
        """Create the Login Widget and attach it to our main window"""
        self.mLoginWindow.show()
        self.setWindowTitle("Login")
        self.setCentralWidget(self.mLoginWindow)
        # Resize the window to widget size
        self.setFixedSize(self.mLoginWindow.size())
        self.mLoginWindow.buttonLogin.rejected.connect(QApplication.exit)

    def start_chat_window(self, seed):
        """ Create the Chat Widget and attach it to our main window"""
        self.setWindowTitle("Messenger")
        self.setCentralWidget(self.mChatWindow)
        # Resize the window to widget size
        self.setFixedSize(self.mChatWindow.size())
        self.mChatWindow.start_showing(seed)

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
