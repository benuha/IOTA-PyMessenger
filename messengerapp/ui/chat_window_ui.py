import datetime
import logging
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem, QMessageBox, QErrorMessage
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
            name, acc_addr = acc_text.split("@")
            self.add_contact(name, acc_addr)

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
                 db_manager):
        """ Showing a simple chat window with user's contacts and current/previous chat messages """
        super(ChatWindow, self).__init__(parent)
        self.setupUi(self)
        self.application = application
        self.db_manager = db_manager

        self.db_account = None
        self.selected_contact_addr = None
        self.buttonSend.clicked.connect(self.on_button_send_click)

        # Init Add Acc dialog
        self.progressBar.hide()
        self.addContactDialog = AddContactWidget(self, fn_add_contact=self.add_new_contact_to_acc)
        self.addAccountDialog = AddAccountWidget(self, fn_add_acc=self.on_new_account_added)
        self.buttonAddFriend.clicked.connect(self.on_open_search_contact_dialog)

        # Fire off the action when user select an acc item on friend list
        self.listContacts.currentItemChanged.connect(self.on_select_contact)

        # Wait for it to be called
        self.hide()

    def start_showing(self, seed):
        self.show()
        self.progressBar.show()

        self.application.set_seed(seed)

        logger.info("Get Acc for seed: {}".format(seed))
        self.db_account = self.db_manager.search_account(seed)

        if self.db_account is not None:
            self.load_account()
        else:
            self.addAccountDialog.show()

    def on_new_account_added(self, acc_name):
        self.addAccountDialog.hide()
        self.progressBar.show()
        # Init the account and attach to Tangle
        self.application.init_account(acc_name,
                                      # if success:
                                      self.fn_on_account_created,
                                      # if error:
                                      lambda err_value: self.fn_on_account_creation_failed(acc_name, err_value))

    def fn_on_account_created(self, new_account):
        self.progressBar.hide()
        self.db_account = new_account
        self.db_manager.store_account(new_account)
        self.load_account()

    def fn_on_account_creation_failed(self, acc_name, err_value):
        dialog_action = self.on_show_error_message(
            "Failed to attach account to Tangle:\n{}.\nRetry now..".format(err_value), capture_action=True)
        if dialog_action == QMessageBox.Yes:
            self.application.init_account(acc_name,
                                          self.fn_on_account_created,
                                          fn_on_failed_callback=self.fn_on_account_creation_failed)
        else:
            # Well Don't know what to do here
            self.close()

    def load_account(self):
        """ Retrieve the contacts of this account
        """
        logger.info("Load account: {}".format(self.db_account.address))
        self.labelAccName.setText("{}@{}".format(self.db_account.name, self.db_account.address))
        self.application.get_qpixmap_identicon(self.db_account.address.__str__(), lambda pix: self.labelAccImage.setPixmap(pix))

        contacts = self.db_account.get_list_contacts()
        for contact in contacts:
            self.add_contact_to_list(contact.name, contact.contact_addr)

        # Query for messages history FIXME
        self.application.query_messages_from_tangle(delayed=False)

    def on_select_contact(self, current_selected, previous_selected):
        # Begin chatting
        logger.info("Select contact: {}".format(current_selected.whatsThis().__str__()))
        self.selected_contact_addr = current_selected.whatsThis().__str__()
        messages = self.application.get_messages_for_contact(self.selected_contact_addr)
        self.got_messages_callback(messages)

    def on_button_send_click(self):
        plain_message = self.textChatMessage.toPlainText().__str__()
        if plain_message == "":
            logger.error("Message chat is empty!")
            return

        if self.selected_contact_addr is None:
            logger.info("You must select one address to start messaging")
            self.on_show_error_message("You must select a contact to start messaging")
            return

        new_message = self.application.create_new_message(
            from_addr_str=self.db_account.address.__str__(),
            to_addr_str=self.selected_contact_addr,
            text=self.textChatMessage.toPlainText().__str__(),
        )
        self.add_message_to_chat(self.db_account.name, new_message, is_attached=False)
        self.on_send_message(plain_message)

    def on_send_message(self, new_message):
        if new_message is None:
            raise ValueError("Message to send cannot be empty!")

        self.progressBar.show()
        self.application.send_message_to_tangle(
            message=new_message,
            fn_on_result=self.on_sending_message_finished,
            fn_on_error=lambda unsent_message, err_val:
                self.resend_message_on_error(unsent_message,
                                             self.on_show_error_message(
                                                 "Failed to send message to Tangle: \n{}\n\nRetry ?".format(
                                                     err_val),
                                                 capture_action=True)
                                             )
        )

    def resend_message_on_error(self, unsent_message, error_dialog_action):
        if error_dialog_action is not None and error_dialog_action == QMessageBox.Yes:
            self.on_send_message(unsent_message)
        else:
            # Do nothing
            self.textChatMessage.clear()

    def on_show_error_message(self, err_text, capture_action=False):
        if not capture_action:
            error_dialog = QMessageBox(self)
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("{}".format(err_text))
            error_dialog.show()
        else:
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Question)
            error_dialog.setText("{}".format(err_text))
            error_dialog.setWindowTitle("Warning")
            error_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            # This will blocks until the dialog was closed and return the result
            return error_dialog.exec_()

    def on_sending_message_finished(self, message):
        self.progressBar.hide()
        self.textChatMessage.clear()
        self.add_message_to_chat(message.from_address, message, is_attached=True)

    def got_messages_callback(self, messages=None):
        self.progressBar.hide()
        self.listMessages.clear()
        if messages is None or len(messages) == 0 or self.selected_contact_addr is None:
            return
        for message in messages:
            if message.from_address == self.selected_contact_addr or \
                    message.to_address == self.selected_contact_addr:
                sender_name = self.application.get_addr_name(message.from_address)

                self.add_message_to_chat(sender_name, message, True)

    def add_message_to_chat(self, sender_name, message, is_attached=False):
        """ Add message to QList, return the index of message """
        # Check if message already on the list
        if self.listMessages.size() > 0:
            for

        else:
            msg_label = QListWidgetItem()
            msg_label.setText("{} on {}:".format(sender_name,
                                                 datetime.datetime.fromtimestamp(
                                                     int(message.timestamp)
                                                 ).strftime('%Y-%m-%d %H:%M:%S')))
            self.application.get_qpixmap_identicon(message.from_address,
                                                   lambda pixmap: msg_label.setIcon(QIcon(pixmap)))
            self.listMessages.addItem(msg_label)

            msg_text = QListWidgetItem()
            msg_text.setText(message.text)

            if not is_attached:
                msg_label.setForeground(QColor("gray"))
                msg_text.setForeground(QColor("gray"))
            else:
                msg_label.setForeground(QColor("black"))
                msg_text.setForeground(QColor("black"))

            self.listMessages.addItem(msg_text)

    def on_open_search_contact_dialog(self):
        # self.dialog.exec_()
        self.addContactDialog.editAccSearch.clear()
        self.addContactDialog.show()

    def add_new_contact_to_acc(self, name, acc_addr):
        # Get new contact info from Tangle and add to current account when success
        self.progressBar.show()
        self.application.init_new_contact(contact_name=name, contact_addr=acc_addr,
                                          fn_on_contact_added=self.add_contact_to_list,
                                          fn_on_finished=lambda: self.progressBar.hide(),
                                          fn_on_failed=self.on_show_error_message)

    def add_contact_to_list(self, name, acc_address):
        acc_item = QListWidgetItem()
        acc_item.setText("{}@{}...".format(name, acc_address[0:15]))
        acc_item.setWhatsThis(acc_address)

        self.application.get_qpixmap_identicon(acc_address, lambda pixmap: acc_item.setIcon(QIcon(pixmap)))

        self.listContacts.addItem(acc_item)
        self.progressBar.hide()
