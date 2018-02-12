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
        :return: The first account associated with this seed, otherwise None
        """
        if seed not in self.db_root:
            self.db_root[seed] = Account(seed)
            self.update_all()
            return None
        account = self.db_root[seed]
        addresses = account.get_addresses_list()
        if len(addresses) == 0:
            return None
        return addresses[0]

    def update_all(self):
        zodb_trans.commit()

    def add_account(self, seed, new_address):
        _account = Account(seed)
        self.db_root[seed] = _account
        self.update_all()
        _account.store_new_address(new_address)

    def close(self):
        logger.info("Closing the database")
        self.db.close()
        self.storage.close()


class Account(persistent.Persistent):

    def __init__(self, hashed_seed):
        """ Account in database with persistent seed value. No other protection,
        means You have to hashed your seed in case the database is compromised """
        self.seed = hashed_seed
        self.addresses = []

    def store_new_address(self, address):
        self.addresses.append(address)
        # Mark the record as changed
        self._p_changed = True
        zodb_trans.commit()

    def get_addresses_list(self):
        return self.addresses


class Address(persistent.Persistent):

    def __init__(self, name, address, key_index, public_key, private_key, checksum=None, balance=None):
        """ Account represented by address which generated from user seed and
        attached to tangle. Public/private key are used to encrypt and exchange messages securely over tangle """
        self.address = address
        self.key_index = key_index
        self.public_key = public_key
        self.private_key = private_key
        self.checksum = checksum
        self.balance = balance
        self.name = name
        self.contacts = []

    def add_contact(self, contact):
        self.contacts.append(contact)
        zodb_trans.commit()


class Contacts(persistent.Persistent):

    def __init__(self, contact_addr, public_key):
        """ Contact which associate with an account and shared the public key """
        self.contact_addr = contact_addr
        # Contains list of messages from this contact
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)
        zodb_trans.commit()


class Messages(persistent.Persistent):

    STATUS_SENDING = "message_sending"
    STATUS_SENT = "message_sent"
    STATUS_ERROR = "message_error"
    STATUS_QUEUE = "message_queuing"
    STATUS_POW = "message_pow"

    def __init__(self, from_address, to_address, timestamp, text, message_root, status=STATUS_SENDING):
        self.from_address = from_address
        self.to_address = to_address
        self.timestamp = timestamp
        self.text = text
        self.message_root = message_root
        self.status = status

    def update_status(self, status):
        self.status = status
        self._p_changed = True
        zodb_trans.commit()
