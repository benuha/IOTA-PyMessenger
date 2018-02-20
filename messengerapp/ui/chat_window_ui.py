import datetime
import logging

from PyQt5.QtGui import QPixmap, QIcon, QMovie
from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem
from PyQt5.uic.properties import QtWidgets

from messengerapp.utils import identiconer
from messengerapp.views import mchatwidget, msearchwidget, maccountnamewidget

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AddContactWidget(QDialog, msearchwidget.Ui_Dialog):

    def __init__(self, parent=None, fn_add_contact=None):
        super(AddContactWidget, self).__init__(parent)
        self.setupUi(self)
        self.editAccSearch.clear()
        self.editAccSearch.setFocus()
        # Pass function as object so that we can call it later to add account
        self.add_contact = fn_add_contact
        self.buttonsSearch.accepted.connect(lambda: self.check_account_validated(self.editAccSearch.text().__str__()))

    def check_account_validated(self, acc_text):
        if acc_text is None or "@" not in acc_text:
            self.on_notify_account_not_valid()
        else:
            self.add_contact(acc_text)

    def on_notify_account_not_valid(self):
        self.labelStatus.setText("<font color='red'>{}</font>".format("Account must have these format: name@address"))


class AddAccountWidget(QDialog, maccountnamewidget.Ui_Dialog):
    def __init__(self, parent=None, fn_add_acc=None):
        super(AddAccountWidget, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit.clear()
        self.lineEdit.setFocus()
        # Pass function as object so that we can call it later to add account
        self.add_account = fn_add_acc
        self.buttonBox.accepted.connect(lambda: self.check_account_validated(self.lineEdit.text().__str__()))

    def check_account_validated(self, acc_text):
        if acc_text is None or "@" in acc_text:
            self.on_notify_account_not_valid()
        else:
            self.add_account(acc_text)

    def on_notify_account_not_valid(self):
        self.labelStatus.setText("<font color='red'>{}</font>".format("Account must contain no special character"))


class ChatWindow(QWidget, mchatwidget.Ui_Form):

    def __init__(self, parent,
                 application,
                 fn_get_account_with_seed,
                 fn_init_account_with_seed,
                 fn_send_message,
                 fn_get_contact_from_tangle,
                 fn_get_contacts_list_local):
        """ Showing a simple chat window with user's contacts and current/previous chat messages """
        super(ChatWindow, self).__init__(parent)
        self.setupUi(self)
        self.application = application
        self.get_account_with_seed = fn_get_account_with_seed
        self.init_account_with_seed_and_name = fn_init_account_with_seed
        self.send_message = fn_send_message
        self.fn_get_contact_from_tangle = fn_get_contact_from_tangle
        self.fn_get_contacts_list_local = fn_get_contacts_list_local
        self.db_address = None
        self.seed = None
        self.selected_contact = None
        self.buttonSend.clicked.connect(self.on_send_message_click)

        # Init Add Acc dialog
        self.progressBar.hide()
        self.addContactDialog = AddContactWidget(self, fn_add_contact=self.add_contact_to_list)
        self.addAccountDialog = AddAccountWidget(self, fn_add_acc=self.add_new_account)
        self.buttonAddFriend.clicked.connect(self.on_open_search_contact_dialog)

        # Fire off the action when user select an acc item on friend list
        self.listContacts.currentItemChanged.connect(self.on_select_contact)
        self.hide()

    def start_showing(self, seed):
        self.show()
        self.progressBar.show()
        self.seed = seed
        self.db_address = self.get_account_with_seed(seed)
        if self.db_address is not None:
            self.labelAccName.setText("{}@{}".format(self.db_address.name, self.db_address.address))
            self.labelAccImage.setPixmap(get_pixmap_identicon(self.db_address.address.__str__()))

            # Populate the contacts list from db
            contacts = self.fn_get_contacts_list_local(self.db_address)

            self.application.contacts_list = contacts
            self.application.account = self.db_address

            for contact in contacts:
                acc_item = QListWidgetItem()
                acc_item.setText("{}@{}".format(contact.name, contact.contact_addr))
                acc_item.setIcon(QIcon(get_pixmap_identicon(contact.contact_addr)))
                self.listContacts.addItem(acc_item)

            self.application.filter_messages_from_contact(
                fn_on_messages_callback=self.got_messages_callback
            )

        else:
            self.addAccountDialog.show()

    def add_new_account(self, acc_name):
        self.addAccountDialog.hide()
        self.init_account_with_seed_and_name(self.seed, acc_name)

    def on_select_contact(self, current_selected, previous_selected):
        # TODO Begin chatting
        self.selected_contact = current_selected.text()
        self.application.select_contact(current_selected.text())

    def on_send_message_click(self):
        self.progressBar.show()
        # self.send_message(
        #     self.db_address.seed,
        #     self.db_address.address.__str__(),
        #     self.textChatMessage.toPlainText().__str__(),
        #     None,
        #     self.on_worker_thread_finished)
        self.application.send_message_to_selected_contact(
            self.textChatMessage.toPlainText().__str__(),
            fn_on_finished=self.on_worker_thread_finished,
            fn_on_error=self.on_show_error_message
        )

    def on_show_error_message(self, message):
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage(message)

    def on_worker_thread_finished(self):
        self.progressBar.hide()
        self.textChatMessage.clear()

    def got_messages_callback(self, messages=None):
        self.progressBar.hide()
        if messages is None or len(messages) == 0:
            return
        for message in messages:
            if self.application.message_belong_to_current_account(message):
                msg_label = QListWidgetItem()
                msg_label.setText("{} on {}:".format(message.from_address,
                                                     datetime.datetime.fromtimestamp(
                                                         int(message.timestamp)
                                                     ).strftime('%Y-%m-%d %H:%M:%S')))
                msg_label.setIcon(QIcon(get_pixmap_identicon(message.from_address)))
                self.listMessages.addItem(msg_label)

                msg_text = QListWidgetItem()
                msg_text.setText(message.text)
                self.listMessages.addItem(msg_text)

    def on_open_search_contact_dialog(self):
        # self.dialog.exec_()
        self.addContactDialog.editAccSearch.clear()
        self.addContactDialog.show()

    def add_contact_to_list(self, acc_address):
        logger.info("Add account: {}".format(acc_address))
        name, acc_addr = acc_address.split("@")
        acc_item = QListWidgetItem()
        acc_item.setText(acc_address)
        acc_item.setIcon(QIcon(get_pixmap_identicon(acc_addr)))
        self.listContacts.addItem(acc_item)

        # Connect to tangle to retrieve friend account info
        self.progressBar.show()
        self.fn_get_contact_from_tangle(self.db_address, acc_addr, self.on_worker_thread_finished)
        pass


def get_pixmap_identicon(string_iden):
    logger.info("String iden: {}".format(string_iden))
    identicon_image = identiconer.Identicon(string_iden)
    # Convert from PIL Image -> QImage -> QPixmap
    pixmap = QPixmap(identicon_image.convert_pil_to_qimage())
    return pixmap
