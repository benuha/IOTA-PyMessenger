import base64
import logging
import sys
from time import sleep

from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QImage, QPixmap
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
from messengerapp.utils import mcrypto, identiconer
from messengerapp.utils.qworkersthread import Worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MainApplication:

    def __init__(self, mdb):
        self.db_manager = mdb
        self.seed = None

        # Define the thread pool for long-running processes
        self.threadpool = QThreadPool()
        self.piximaps = {}

    def set_seed(self, seed):
        self.seed = seed

    def init_account(self, acc_name, fn_on_account_created_callback, fn_on_failed_callback):
        """ Create a new Account with seed and name, generate public/private key-pair for message encryption.
        And lastly attached it to Tangle to communicate"""
        worker = Worker(self._create_new_account, self.seed, acc_name)
        worker.signals.result.connect(fn_on_account_created_callback)
        worker.signals.error.connect(lambda errs: fn_on_failed_callback(errs[1]))

        self.threadpool.start(worker)

    def init_new_contact(self, contact_name, contact_addr,
                         fn_on_contact_added, fn_on_finished, fn_on_failed):
        worker = Worker(self._init_new_contact, self.seed, contact_name, contact_addr)
        worker.signals.result.connect(lambda this_contact: self.fn_store_contact_to_db(this_contact, fn_on_contact_added))
        worker.signals.error.connect(lambda errs: fn_on_failed(errs[1]))
        worker.signals.finished.connect(fn_on_finished)
        self.threadpool.start(worker)

    def fn_store_contact_to_db(self, this_contact, fn_contact_added):
        db_account = self.db_manager.search_account(self.seed)
        db_account.add_contact(this_contact)
        fn_contact_added(this_contact.name, this_contact.contact_addr)

    @staticmethod
    def _init_new_contact(seed, contact_name, contact_addr):
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
        except Exception as e:
            logger.exception("Failed to find_transaction with tag: {}".format(contact_addr))
            # Raise again for front-end to capture it
            raise e

    def _create_new_account(self, seed, name):
        logger.info("Start multiprocessing with maximum {} threads".format(self.threadpool.maxThreadCount()))
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
        except Exception as e:
            logger.exception("Failed to create new account using seed: {}".format(seed))
            raise e

    def create_new_message(self,
                           from_addr_str,
                           to_addr_str,
                           text):
        """ Creat a message based on input, encrypt plain-text with recipient public key """
        created_message = Messages(from_address=from_addr_str,
                                   to_address=to_addr_str,
                                   timestamp=get_current_timestamp(),
                                   text="")
        # Get the contact associate with this acc
        acc_contact = self.db_manager.search_for_contact(self.seed, to_addr_str)
        if acc_contact is not None and acc_contact.public_key is not None:
            cipher_text, aes_cipher = mcrypto.message_encryption(json.dumps(text),
                                                                 base64.b64decode(
                                                                     acc_contact.public_key.encode('utf-8')))
            created_message.cipher_text = cipher_text.decode('utf-8')
            created_message.aes_cipher = aes_cipher.decode('utf-8')

        logger.info("Created new message: {}".format(created_message))
        # Store message in db
        logger.info("Store message to db: {}".format(text))
        created_message.text = text
        db_account = self.db_manager.search_account(self.seed)
        db_account.add_message(created_message)
        return created_message

    def send_message_to_tangle(self,
                               message,
                               fn_on_result,
                               fn_on_finished=None,
                               fn_on_error=None):
        """ Sending message to Tangle """
        logger.info("Sending message: {}".format(message))
        # Pass arguments to worker thread and connect comeback events
        worker = Worker(self._send_message_from_thread, self.seed, message.to_address,
                        message.convert_to_dict(), IOTAWrapper.MESS_TAG)
        worker.signals.finished.connect(fn_on_finished)
        worker.signals.result.connect(lambda result: fn_on_result(message))
        worker.signals.error.connect(lambda errs_tuple: fn_on_error(message, errs_tuple[1]))
        # Execute the worker thread
        self.threadpool.start(worker)

    def on_store_all_messages(self, messages):
        # save to db
        db_account = self.db_manager.search_account(self.seed)
        db_account.add_messages(messages)

    def query_messages_from_tangle(self, delayed=False):
        """ Pull new messages off Tangle Net with the app Tag """
        logger.info("Current db messages list: {}".format(len(self.db_manager.search_account(self.seed).get_messages())))
        worker = Worker(self._find_messages, self.seed, delayed)
        worker.signals.result.connect(self.on_store_all_messages)
        # re-run after finished with a time delay
        worker.signals.finished.connect(lambda: self.rerun_the_query(True))
        self.threadpool.start(worker)

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

    def get_qpixmap_identicon(self, string_iden, fn_set_image):
        if len(self.piximaps.keys()) == 0 or self.piximaps.get(string_iden) is None:
            pixmap = self._get_qpixmap_identicon(string_iden)
            # Store the image locally so we can get to it later
            self.piximaps[string_iden] = pixmap
            fn_set_image(pixmap)
        else:
            # Retrive the current Iden image
            fn_set_image(self.piximaps.get(string_iden))

    @staticmethod
    def _get_qpixmap_identicon(string_iden):
        """ Generate the Identicon of the string,
        and convert from PIL Image -> QImage -> QPixmap
        :return QPixmap image"""
        logger.info("String iden: {}".format(string_iden))
        identicon_image = identiconer.create_identicon_pil(ident_str=string_iden)

        imageq = ImageQt(identicon_image)
        # cast PIL.ImageQt object to QImage object -that´s the trick!!!
        qimage = QImage(imageq)
        pixmap = QPixmap(qimage)
        return pixmap

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
        messages = []
        try:
            if must_wait:
                # Wait a bit before rerun it
                sleep(10)
            logger.info("Find messages from Tangle")
            iota_wrapper = IOTAWrapper(seed)
            txs = iota_wrapper.find_transaction()

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
            for m in messages:
                logger.info(m)
        except:
            logger.exception("Failed to find messages with app tag")

        return messages


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
    # form.start_login_window()
    form.start_chat_window(
      "JURCUDDJDL9WWVYQDUJAHVSPJCOEIJJURNVYHEZAXTKRSVLZUIILVWJBPOQJLLYOWFRMHBSHUENXQNFMI"
        # "9MKUUMIQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLRUJOJC9QEXWCIL9HOUUWMDCAWGFAFSJM"
    )

    # Execute the app and wait for interaction
    sys.exit(app.exec_())


if __name__ == '__main__':
    # Start the gui
    run()
