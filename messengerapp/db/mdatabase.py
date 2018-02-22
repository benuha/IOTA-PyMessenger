import logging

import ZODB
import ZODB.FileStorage
import persistent
from os import path
import transaction as zodb_trans

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBManager:

    def __init__(self, db_name="mdb", storage_location=None):
        logger.info("Open connection to Zope-Object database")
        if storage_location is None:
            storage_location = path.dirname(path.dirname(path.realpath(__file__)))
        self.db_name = db_name + ".fs"
        self.storage = ZODB.FileStorage.FileStorage(path.join(storage_location, db_name))
        self.db = ZODB.DB(self.storage)
        # Get the root object dict, this's where we store our data
        self.db_root = self.db.open().root()

    def search_account(self, seed):
        """
        Search local db for account with given seed
        :return: account associated with this seed, otherwise None
        """
        if seed not in self.db_root:
            return None

        account = self.db_root[seed]
        return account

    def search_for_contact(self, seed, contact_addr):
        _acc = self.search_account(seed)
        if _acc is None:
            return None

        return _acc.get_contact_with_addr(contact_addr)

    def store_account(self, _account):
        _seed = _account.seed
        self.db_root[_seed] = _account
        self.update_all()

    def close(self):
        logger.info("Closing the database")
        self.db.close()
        self.storage.close()

    def update_all(self):
        zodb_trans.commit()


class Account(persistent.Persistent):

    def __init__(self, name, seed, address, key_index, public_key, private_key, checksum=None, balance=None):
        """ Account represented by address which generated from user seed and
        attached to tangle. Public/private key are used to encrypt and exchange messages securely over tangle """
        self.seed = seed
        self.address = address
        self.key_index = key_index
        self.public_key = public_key
        self.private_key = private_key
        self.checksum = checksum
        self.balance = balance
        self.name = name
        self.contacts = []
        self.attached = False
        # Contains list of messages from this account
        self.messages = []

    def get_messages(self):
        if not hasattr(self, 'messages'):
            self.messages = []
        return self.messages

    def add_message(self, message):
        if not hasattr(self, 'messages'):
            self.messages = []
        self.messages.append(message)
        # Mark the record as changed
        self._p_changed = True
        zodb_trans.commit()

    def add_messages(self, messages_list):
        if not hasattr(self, 'messages'):
            self.messages = []
        for message in messages_list:
            equal = False
            for db_mess in self.messages:
                if db_mess == message:
                    equal = True
                    break
            if not equal:
                self.messages.append(message)

    def set_account_status_attached(self):
        """Change the status of account to Attached to Tangled.
         This function doesn't actually commit the change to db, yet.
         """
        self.attached = True

    def add_contact(self, contact):
        self.contacts.append(contact)
        # Mark the record as changed
        self._p_changed = True
        zodb_trans.commit()

    def get_list_contacts(self):
        return self.contacts

    def get_contact_with_addr(self, contact_addr):
        if len(self.contacts) == 0:
            return None

        for contact in self.contacts:
            if contact.contact_addr == contact_addr:
                return contact


class Contacts(persistent.Persistent):

    def __init__(self, contact_addr, name, public_key):
        """ Contact which associate with an account and shared the public key """
        self.contact_addr = contact_addr
        self.name = name
        self.public_key = public_key


class Messages(persistent.Persistent):

    STATUS_SENDING = "message_sending"
    STATUS_SENT = "message_sent"
    STATUS_ERROR = "message_error"
    STATUS_QUEUE = "message_queuing"
    STATUS_POW = "message_pow"

    def __init__(self, from_address, to_address, timestamp, text, cipher_text=None, aes_cipher=None,
                 message_root=None, status=STATUS_SENDING):
        self.from_address = from_address
        self.to_address = to_address
        self.timestamp = timestamp
        self.text = text
        self.cipher_text = cipher_text
        self.aes_cipher = aes_cipher
        self.message_root = message_root
        self.status = status

    def is_valid_message(self):
        return self.from_address is not None and \
            self.to_address is not None and \
            self.timestamp is not None

    def update_status(self, status):
        self.status = status
        self._p_changed = True
        zodb_trans.commit()

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def convert_to_dict(self):
        return {
            "from_address": self.from_address,
            "to_address": self.to_address,
            "timestamp": self.timestamp,
            "text": self.text,
            "cipher_text": self.cipher_text,
            "aes_cipher": self.aes_cipher,
            "message_root": self.message_root,
            "status": self.status
        }
