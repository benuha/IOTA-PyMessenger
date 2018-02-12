from unittest import TestCase

import transaction as zodb_trans

from messengerapp.db.mdatabase import Account, Contacts, Messages, Address, DBManager


class MDatabaseTest(TestCase):

    def setUp(self):
        self.db_man = DBManager()
        self.db_root = self.db_man.db_root
        self.predefined_seed = "9MKUUMIQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLRUJOJC9QEXWCIL9HOUUWMDCAWGFAFSJM"
        self.predefined_address = "ZJLUDW9MCJSQKMCESEHJHZKOPZVHNNWKO9IKHUPJMFHXRVVAUNEIQNYOKGYM9DYGMZZNHAIHZYAOTAKAB"

    def _test_add_account(self):
        account = Account(hashed_seed=self.predefined_seed)
        self.assertFalse(self.predefined_seed in self.db_root)
        self.db_root[self.predefined_seed] = account
        zodb_trans.commit()
        self.assertTrue(self.predefined_seed in self.db_root)
        self.assertTrue(type(self.db_root[self.predefined_seed] is Account))

    def _test_add_address(self):
        self.assertIsNotNone(self.db_root[self.predefined_seed])
        self.assertTrue(len(self.db_root[self.predefined_seed].get_addresses_list()) == 0)

        address = Address(
            name="benuha",
            address=self.predefined_address,
            key_index=7,
            checksum="DRNERWHDA",
        )
        self.db_root[self.predefined_seed].store_new_address(address)
        self.assertTrue(len(self.db_root[self.predefined_seed].get_addresses_list()) == 1)

    def test_add_contact(self):
        pass

    def tearDown(self):
        self.db_man.close()
