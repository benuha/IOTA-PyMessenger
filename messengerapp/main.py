import base64
import logging
import sys
from time import sleep
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication
from iota import get_current_timestamp
import iota
import json
from messengerapp.db import mdatabase
from messengerapp.db.mdatabase import DBManager, Contacts, Messages
from messengerapp.ui.chat_window_ui import ChatWindow
from messengerapp.ui.login_window_ui import LoginWindow
from messengerapp.ui.main_window_ui import MainWindow
from messengerapp.iotacore.iotawrapper import IOTAWrapper
from messengerapp.utils import mcrypto
from messengerapp.utils.qworkersthread import Worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the thread pool for long-running processes
threadpool = QThreadPool()


# def get_account_with_seed(seed=_seed):
#     try:
#         logger.info("Get Acc for seed: {}".format(seed))
#         db_account = db_manager.search_account(seed)
#
#         if db_account is not None:
#             # Check tangle for this account address by tag
#             get_current_account_transactions(db_account)
#             pass
#         return db_account
#     except:
#         logger.exception("Cannot search db for account with seed: {}".format(seed))
#     return None
#
#
# def get_current_account_transactions(cur_account):
#     worker = Worker(_get_current_account_txs, cur_account)
#     threadpool.start(worker)
#
#
# def _get_current_account_txs(cur_account):
#     try:
#         iota_wrapper = IOTAWrapper(cur_account.seed)
#         # Find all transactions with tag is current address
#         transactions_list = iota_wrapper.find_transaction(cur_account.address.__str__())
#         # if the account has no transaction, it's not been attached to tangle yet
#         if transactions_list is None or len(transactions_list) == 0:
#             logger.info("No transaction attached from this account: {}".format(cur_account.address))
#             # re-attach to tangle
#             message = {
#                 "name": cur_account.name,
#                 "account_address": cur_account.address.__str__(),
#                 "public_key": cur_account.public_key.decode()
#             }
#             logger.info("Send Message to address: {}\n{}".format(cur_account.address, message))
#             transfer = iota_wrapper.create_new_transaction(
#                 address=cur_account.address.__str__(),
#                 message=json.dumps(message),
#                 raw_tag=iota_wrapper.get_tags(cur_account.address.__str__())
#             )
#             iota_wrapper.send_transaction(transfer)
#         else:
#             logger.info("Already attached to Tangle: {}".format(cur_account.address))
#
#     except:
#         logger.exception("Failed to get current account transactions: {}".format(cur_account.address))
#
#
# def create_new_account(seed, name):
#     """ Connect to tangle and request a new address for the current seed """
#     try:
#         iota_wrapper = IOTAWrapper(seed)
#         response = iota_wrapper.create_new_address()
#         m_address = Address(response,
#                             balance=response.balance,
#                             key_index=response.key_index,
#                             security_level=response.security_level)
#
#         private_key_b64, public_key_b64 = iota_wrapper.generate_rsa_key_pair()
#         db_address = mdatabase.Address(name=name,
#                                        seed=seed,
#                                        address=m_address.address,
#                                        key_index=m_address.key_index,
#                                        public_key=public_key_b64,
#                                        private_key=private_key_b64,
#                                        checksum=m_address.checksum,
#                                        balance=m_address.balance)
#         db_manager.add_account(seed, db_address)
#
#         # Public the public key of this account to tangle using account address as tag
#         m_tag = iota_wrapper.get_tags(db_address.address.__str__())
#         attach_to_tangle(seed,
#                          name,
#                          db_address.address.__str__(),
#                          public_key_b64.decode(),  # decode to string
#                          m_tag
#                          )
#
#         return db_address
#     except:
#         logger.exception("Failed to create new account using seed: {}".format(seed))
#     pass
#
#
# def attach_to_tangle(seed, acc_name, address_str, public_key, tag):
#     # Broadcast public address of the account, so other can use this public key to chat with user
#     message = {
#         "name": acc_name,
#         "account_address": address_str,
#         "public_key": public_key
#     }
#     send_message_to_tangle(seed, address_str, message, tag)
#
#
# def get_contact_from_tangle(cur_address, acc_address, on_result=print, on_finished=None):
#     # Filter by Tag for message that an account has publish
#     # the tag is the acc_address
#     worker = Worker(_find_contact_by_tag, cur_address, acc_address)
#     worker.signals.result.connect(on_result)
#     if on_finished is not None:
#         worker.signals.finished.connect(on_finished)
#     # Execute the worker thread
#     threadpool.start(worker)
#
#
# def send_message_to_tangle(seed, to_address_str, message, tag=None, on_finished=None):
#     logger.info("Multiprocessing with maximum {} threads".format(threadpool.maxThreadCount()))
#     # Pass arguments to worker thread and connect comeback events
#     worker = Worker(_send_message_from_thread, seed, to_address_str, message, tag)
#     worker.signals.finished.connect(on_finished)
#     # Execute the worker thread
#     threadpool.start(worker)
#
#
# def _on_found_contacts(cur_address, contact_address, contacts_list):
#     for contact in contacts_list:
#         db_contact = Contacts(contact_address, contact.get("name"),
#                               contact["public_key"])
#         cur_address.add_contact(db_contact)
#
#
# def _find_contact_by_tag(current_address, acc_address):
#     if acc_address is None:
#         return
#     try:
#         iota_wrapper = IOTAWrapper(current_address.seed)
#         logger.info("Find account by tag as address: {}".format(acc_address))
#         transactions_dict = iota_wrapper.find_transaction(acc_address)
#
#         _on_found_contacts(current_address, acc_address, transactions_dict)
#         return transactions_dict
#     except:
#         logger.exception("Failed to find_transaction with tag: {}".format(acc_address))
#
#
# def _send_message_from_thread(seed, to_address_str, message=None, tag=None):
#     if to_address_str is None or message is None:
#         return
#
#     iota_wrapper = IOTAWrapper(seed)
#     logger.info("Send Message to address: {}\n{}".format(to_address_str, message))
#     transfer = iota_wrapper.create_new_transaction(
#         address=to_address_str,
#         message=json.dumps(message),
#         raw_tag=tag
#     )
#     iota_wrapper.send_transaction(transfer)
#
#
# def login_account_with_seed(seed, form=None):
#     if form is not None:
#         form.start_chat_window(seed)


def run():
    # Create a new instance of QApplication
    app = QApplication(sys.argv)
    # Set the form to be our design MainWindow
    form = MainWindow()

    mLoginWindow = LoginWindow(form,
                               fn_login_account_with_seed=form.start_chat_window)

    # Define database management object
    db_man = DBManager()

    mChatWindow = ChatWindow(form,
                             application=MainApplication(db_man),
                             db_manager=db_man)

    form.mChatWindow = mChatWindow
    form.mLoginWindow = mLoginWindow
    form.show()

    # TODO For Debug: start chat_window right away with a predefine seed
    form.start_login_window()
    # form.start_chat_window(
    #     # "JURCUDDJDL9WWVYQDUJAHVSPJCOEIJJURNVYHEZAXTKRSVLZUIILVWJBPOQJLLYOWFRMHBSHUENXQNFMI"
    #     "9MKUUMIQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLRUJOJC9QEXWCIL9HOUUWMDCAWGFAFSJM"
    # )

    # Execute the app and wait for interaction
    sys.exit(app.exec_())


class MainApplication:

    def __init__(self, mdb):
        self.db_manager = mdb
        self.seed = None

    def set_seed(self, seed):
        self.seed = seed

    def init_account(self, acc_name, fn_on_account_created_callback):
        """ Create a new Account with seed and name, generate public/private key-pair for message encryption.
        And lastly attached it to Tangle to communicate"""
        worker = Worker(self._create_new_account, self.seed, acc_name)
        worker.signals.result.connect(fn_on_account_created_callback)
        worker.signals.error.connect(lambda: fn_on_account_created_callback(None))

        threadpool.start(worker)

    def init_new_contact(self, contact_name, contact_addr, fn_on_contact_added):
        worker = Worker(self._init_new_contact, self.seed, contact_name, contact_addr)
        worker.signals.finished.connect(lambda: fn_on_contact_added(contact_name, contact_addr))
        worker.signals.result.connect(self.fn_add_new_contact)
        # Do we need error checking here?
        # worker.signals.error.connect(print)

        threadpool.start(worker)

    def _init_new_contact(self, seed, contact_name, contact_addr):
        # Get this contact info from Tangle by filter for its Tag as addr
        try:
            iota_wrapper = IOTAWrapper(seed)
            logger.info("Find account by tag as address: {}".format(contact_addr))
            transactions_dict = iota_wrapper.find_transaction(tag=contact_addr)

            contact = transactions_dict[0]
            this_contact = Contacts(contact_addr,
                                    contact_name,
                                    contact["public_key"])

            return this_contact
        except:
            logger.exception("Failed to find_transaction with tag: {}".format(contact_addr))

    def fn_add_new_contact(self, this_contact):
        db_account = self.db_manager.search_account(self.seed)
        db_account.add_contact(this_contact)

    def _create_new_account(self, seed, name):
        logger.info("Start multiprocessing with maximum {} threads".format(threadpool.maxThreadCount()))
        logger.info("Create new account: {}\nSeed: {}".format(name, seed))
        try:
            iota_wrapper = IOTAWrapper(seed)
            response = iota_wrapper.create_new_address()
            m_address = iota.Address(response,
                                     balance=response.balance,
                                     key_index=response.key_index,
                                     security_level=response.security_level)

            # Generate key-pair used in message encryption
            private_key_b64, public_key_b64 = mcrypto.generate_rsa_key_pair()
            db_address = mdatabase.Account(name=name,
                                           seed=seed,
                                           address=m_address.address,
                                           key_index=m_address.key_index,
                                           public_key=public_key_b64,
                                           private_key=private_key_b64,
                                           checksum=m_address.checksum,
                                           balance=m_address.balance)

            # Public the public key of this account to tangle using account address as tag
            m_tag = iota_wrapper.get_tryte_tag(db_address.address.__str__())

            # Attach new Account to Tangle
            # Same as sending new message with zero IOTA value
            message = {
                "name": name,
                "account_address": db_address.address.__str__(),
                "public_key": public_key_b64.decode()
            }

            response = self._send_message_from_thread(seed, db_address.address.__str__(), message, m_tag)

            if response is not None:
                bundle = iota.Bundle(response['bundle'])
                print("Bundle Hash: {}\nFrom Address: {}".format(bundle.hash,
                                                                 bundle.transactions[0].address,
                                                                 bundle.transactions[0].tag))
                db_address.set_account_status_attached()

            return db_address
        except:
            logger.exception("Failed to create new account using seed: {}".format(seed))

    def send_message_to_selected_contact(self,
                                         from_addr_str,
                                         to_addr_str,
                                         text,
                                         fn_on_finished=None,
                                         fn_on_error=None):

        create_message = Messages(from_address=from_addr_str,
                                  to_address=to_addr_str,
                                  timestamp=get_current_timestamp(),
                                  text="")

        # Get the contact associate with this acc
        acc_contact = self.db_manager.search_for_contact(self.seed, to_addr_str)
        if acc_contact is not None and acc_contact.public_key is not None:
            cipher_text, aes_cipher = mcrypto.message_encryption(json.dumps(text),
                                                                 base64.b64decode(acc_contact.public_key.encode('utf-8')))
            create_message.cipher_text = cipher_text.decode('utf-8')
            create_message.aes_cipher = aes_cipher.decode('utf-8')

        logger.info("Sending message: {}".format(create_message))
        # Pass arguments to worker thread and connect comeback events
        worker = Worker(self._send_message_from_thread, self.seed, to_addr_str,
                        create_message.convert_to_dict(), IOTAWrapper.MESS_TAG)
        worker.signals.finished.connect(fn_on_finished)
        worker.signals.result.connect(lambda: self.on_store_message(create_message, text))
        # Execute the worker thread
        threadpool.start(worker)

    def on_store_message(self, created_message, plain_text):
        logger.info("Store message to db: {}".format(plain_text))
        created_message.text = plain_text
        db_account = self.db_manager.search_account(self.seed)
        db_account.add_message(created_message)

    def on_store_all_messages(self, messages):
        # save to db
        db_account = self.db_manager.search_account(self.seed)
        db_account.add_messages(messages)

    def query_messages_from_tangle(self, delayed=False):
        """ Pull new messages off Tangle Net with the app Tag """
        worker = Worker(self._find_messages, self.seed, delayed)
        worker.signals.result.connect(self.on_store_all_messages)
        # re-run after finished with a time delay
        worker.signals.finished.connect(lambda: self.rerun_the_query(True))
        threadpool.start(worker)

    def rerun_the_query(self, delayed=False):
        # Re-run the query
        self.query_messages_from_tangle(delayed)

    def get_messages_for_contact(self, contact_addr):
        db_account = self.db_manager.search_account(self.seed)

        contact_messages = []
        for message in db_account.messages:
            if message.from_address == contact_addr:
                real_text = mcrypto.message_decryption(
                    cipher_text=message.cipher_text,
                    aes_cipher=message.aes_cipher,
                    private_key=base64.b64decode(db_account.private_key.decode('utf-8'))
                )
                message.text = real_text
                contact_messages.append(message)
            elif message.to_address == contact_addr:
                contact_messages.append(message)

        return contact_messages

    def get_addr_name(self, addr):
        db_account = self.db_manager.search_account(self.seed)
        if db_account.address == addr:
            return db_account.name
        else:
            for contact in db_account.get_list_contacts():
                if contact.contact_addr == addr:
                    return contact.name
        return "unknown"

    @staticmethod
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
        return iota_wrapper.send_transaction(transfer)

    @staticmethod
    def _find_messages(seed, must_wait=False):
        try:
            if must_wait:
                # Wait a bit before rerun it
                sleep(3)
            logger.info("Find messages from Tangle")
            iota_wrapper = IOTAWrapper(seed)
            txs = iota_wrapper.find_transaction()

            messages = []
            for transaction in txs:
                try:
                    message = Messages(
                        from_address=transaction.get("from_address"),
                        to_address=transaction.get("to_address"),
                        timestamp=transaction.get("timestamp"),
                        text=transaction.get("text"),
                        cipher_text=transaction.get("cipher_text").encode('utf-8'),
                        aes_cipher=transaction.get("aes_cipher").encode('utf-8'),
                        message_root=transaction.get("message_root"),
                        status=transaction.get("status")
                    )
                    if message.is_valid_message():
                        messages.append(message)
                except AttributeError:
                    logger.error("Attribute Error!: {}".format(transaction))
                    pass
                except:
                    logger.error("Cannot extract message from transaction: {}".format(transaction))

            messages.sort(key=lambda x: x.timestamp)
            logger.info(messages)
            return messages
        except:
            logger.exception("Failed to find messages with app tag")


if __name__ == '__main__':
    # Start the gui
    run()
