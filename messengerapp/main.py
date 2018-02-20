import logging
import sys

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication
from iota import Address, get_current_timestamp
import json
from messengerapp.db import mdatabase
from messengerapp.db.mdatabase import DBManager, Contacts, Messages
from messengerapp.ui.chat_window_ui import ChatWindow
from messengerapp.ui.login_window_ui import LoginWindow
from messengerapp.ui.main_window_ui import MainWindow
from messengerapp.iotacore.iotawrapper import IOTAWrapper
from messengerapp.utils.qworkersthread import Worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_seed = "9MKUUMIQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLRUJOJC9QEXWCIL9HOUUWMDCAWGFAFSJM"


# Define database management object
db_manager = DBManager()

# Define the thread pool for long-running processes
threadpool = QThreadPool()


def get_account_with_seed(seed=_seed):
    try:
        logger.info("Get Acc for seed: {}".format(seed))
        db_account = db_manager.search_account(seed)

        if db_account is not None:
            # Check tangle for this account address by tag
            get_current_account_transactions(db_account)
        return db_account
    except:
        logger.exception("Cannot search db for account with seed: {}".format(seed))
    return None


def get_current_account_transactions(cur_account):
    worker = Worker(_get_current_account_txs,  cur_account)

    threadpool.start(worker)


def _get_current_account_txs(cur_account):
    try:
        iota_wrapper = IOTAWrapper(cur_account.seed)
        # Find all transactions with tag is current address
        transactions_list = iota_wrapper.find_transaction(cur_account.address.__str__())
        # if the account has no transaction, it's not been attached to tangle yet
        if transactions_list is None or len(transactions_list) == 0:
            logger.info("No transaction attached from this account: {}".format(cur_account.address))
            # re-attach to tangle
            message = {
                "name": cur_account.name,
                "account_address": cur_account.address.__str__(),
                "public_key": cur_account.public_key.decode()
            }
            logger.info("Send Message to address: {}\n{}".format(cur_account.address, message))
            transfer = iota_wrapper.create_new_transaction(
                address=cur_account.address.__str__(),
                message=json.dumps(message),
                raw_tag=iota_wrapper.get_tags(cur_account.address.__str__())
            )
            iota_wrapper.send_transaction(transfer)
        else:
            logger.info("Already attached to Tangle: {}".format(cur_account.address))

    except:
        logger.exception("Failed to get current account transactions: {}".format(cur_account.address))


def create_new_account(seed, name):
    """ Connect to tangle and request a new address for the current seed """
    try:
        iota_wrapper = IOTAWrapper(seed)
        response = iota_wrapper.create_new_address()
        m_address = Address(response,
                            balance=response.balance,
                            key_index=response.key_index,
                            security_level=response.security_level)

        private_key_b64, public_key_b64 = iota_wrapper.generate_rsa_key_pair()
        db_address = mdatabase.Address(name=name,
                                       seed=seed,
                                       address=m_address.address,
                                       key_index=m_address.key_index,
                                       public_key=public_key_b64,
                                       private_key=private_key_b64,
                                       checksum=m_address.checksum,
                                       balance=m_address.balance)
        db_manager.add_account(seed, db_address)

        # Public the public key of this account to tangle using account address as tag
        m_tag = iota_wrapper.get_tags(db_address.address.__str__())
        attach_to_tangle(seed,
                         name,
                         db_address.address.__str__(),
                         public_key_b64.decode(),  # decode to string
                         m_tag
                         )

        return db_address
    except:
        logger.exception("Failed to create new account using seed: {}".format(seed))
    pass


def attach_to_tangle(seed, acc_name, address_str, public_key, tag):
    # Broadcast public address of the account, so other can use this public key to chat with user
    message = {
        "name": acc_name,
        "account_address": address_str,
        "public_key": public_key
    }
    send_message_to_tangle(seed, address_str, message, tag)


def get_contacts_from_local(cur_address):
    return cur_address.get_list_contacts()


def get_contact_from_tangle(cur_address, acc_address, on_result=print, on_finished=None):
    # Filter by Tag for message that an account has publish
    # the tag is the acc_address
    worker = Worker(_find_contact_by_tag, cur_address, acc_address)
    worker.signals.result.connect(on_result)
    if on_finished is not None:
        worker.signals.finished.connect(on_finished)
    # Execute the worker thread
    threadpool.start(worker)


def send_message_to_tangle(seed, to_address_str, message, tag=None, on_finished=None):
    logger.info("Multiprocessing with maximum {} threads".format(threadpool.maxThreadCount()))
    # Pass arguments to worker thread and connect comeback events
    worker = Worker(_send_message_from_thread, seed, to_address_str, message, tag)
    worker.signals.finished.connect(on_finished)
    # Execute the worker thread
    threadpool.start(worker)


def _on_found_contacts(cur_address, contact_address, contacts_list):
    for contact in contacts_list:
        db_contact = Contacts(contact_address, contact.get("name"),
                              contact["public_key"])
        cur_address.add_contact(db_contact)


def _find_contact_by_tag(current_address, acc_address):
    if acc_address is None:
        return
    try:
        iota_wrapper = IOTAWrapper(current_address.seed)
        logger.info("Find account by tag as address: {}".format(acc_address))
        transactions_dict = iota_wrapper.find_transaction(acc_address)

        _on_found_contacts(current_address, acc_address, transactions_dict)
        return transactions_dict
    except:
        logger.exception("Failed to find_transaction with tag: {}".format(acc_address))


def _send_message_from_thread(seed, to_address_str, message=None, tag=None):
    if to_address_str is None or message is None:
        return

    iota_wrapper = IOTAWrapper(seed)
    logger.info("Send Message to address: {}\n{}".format(to_address_str, message))
    transfer = iota_wrapper.create_new_transaction(
        address=to_address_str,
        message=json.dumps(message),
        raw_tag=tag
    )
    iota_wrapper.send_transaction(transfer)


def login_account_with_seed(seed, form=None):
    if form is not None:
        form.start_chat_window(seed)


def run():
    # Create a new instance of QApplication
    app = QApplication(sys.argv)
    # Set the form to be our design MainWindow
    form = MainWindow()

    mLoginWindow = LoginWindow(form,
                               fn_login_account_with_seed=login_account_with_seed)

    mChatWindow = ChatWindow(form,
                             application=MainApplication(),
                             fn_get_account_with_seed=get_account_with_seed,
                             fn_init_account_with_seed=create_new_account,
                             fn_send_message=send_message_to_tangle,
                             fn_get_contact_from_tangle=get_contact_from_tangle,
                             fn_get_contacts_list_local=get_contacts_from_local)

    form.mChatWindow = mChatWindow
    form.mLoginWindow = mLoginWindow
    form.show()

    form.start_login_window()

    # Execute the app and wait for interaction
    sys.exit(app.exec())


class MainApplication:

    def __init__(self):
        self.account = None
        self.contacts_list = []
        self.selected_contact = None

    def set_contact_list(self, mlist):
        self.contacts_list = mlist

    def select_contact(self, contact_addr):
        for contact in self.contacts_list:
            if contact.contact_addr in contact_addr:
                self.selected_contact = contact
                logger.info("Select contact: {}".format(contact.contact_addr))
                break

    def send_message_to_selected_contact(self, message,
                                         fn_on_finished=None,
                                         fn_on_error=None):
        create_message = {
            "timestamp": get_current_timestamp(),
            "text": message,
            "from": self.account.address.__str__(),
            "to": self.selected_contact.contact_addr
        }

        send_message_to_tangle(self.account.seed,
                               self.selected_contact.contact_addr,
                               create_message,
                               tag=IOTAWrapper.MESS_TAG,
                               on_finished=fn_on_finished
                               )

    def filter_messages_from_contact(self, fn_on_messages_callback):
        worker = Worker(_find_messages, self.account.seed)
        worker.signals.result.connect(fn_on_messages_callback)
        worker.signals.finished.connect(fn_on_messages_callback)
        threadpool.start(worker)

    def message_belong_to_current_account(self, message):
        return message.from_address == self.account.address.__str__()


def _find_messages(seed):
    try:
        iota_wrapper = IOTAWrapper(seed)
        txs = iota_wrapper.find_transaction()

        messages = []
        for transaction in txs:
            try:
                message = Messages(
                    from_address=transaction.get("from"),
                    to_address=transaction.get("to"),
                    timestamp=transaction.get("timestamp"),
                    text=transaction.get("text")
                )
                if message.is_valid_message():
                    messages.append(message)
            except:
                logger.error("Cannot extract message from transaction: {}".format(transaction))

        messages.sort(key=lambda x: x.timestamp)
        return messages
    except:
        logger.exception("Failed to find messages with app tag")


if __name__ == '__main__':
    # Start the gui
    run()
