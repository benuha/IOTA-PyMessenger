from unittest import TestCase
from messengerapp.db.mdatabase import Account, Contacts, Messages, DBManager


class MDatabaseTest(TestCase):
    """This test is for db specific and only focus on checking ZODB """

    def setUp(self):
        self.db_man = DBManager()
        self.predefined_1 = {
            "seed": "9MKUUMIQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLRUJOJC9QEXWCIL9HOUUWMDCAWGFAFSJM",
            "address": "SFKKFEJMOPDTVOQXFFVRACCVAYPWZNXDXQUK9KSRXSKCDSBIVZHVPLUPOI9SKOTF9SJ9GAUEDVEEUVGXD"
        }
        self.predefined_2 = {
            "seed": "JURCUDDJDL9WWVYQDUJAHVSPJCOEIJJURNVYHEZAXTKRSVLZUIILVWJBPOQJLLYOWFRMHBSHUENXQNFMI"
        }

    def _test_check_account(self):
        db_account = self.db_man.search_account(self.predefined_1["seed"])

        print(db_account.address)
        self.assertTrue(self.predefined_1["address"], db_account.address)

    def test_check_messages_list(self):
        db_account = self.db_man.search_account(self.predefined_2["seed"])
        print(db_account.address)
        self.assertTrue(db_account.get_messages is not None)

        # clean messages list
        # db_account.get_messages().clear()
        # db_account.update_all()
        print(len(db_account.get_messages()))
        for message in db_account.get_messages():
            print(message.convert_to_dict())
            # if "NZIVFIVOZSORKGMIEADEQXXGKVLNZALZCNVZPVZZPDSYGSF9PTLVWVSCCRGXOHSESMZYXTLXDXVQBYEJX" == message.from_address:
            #     db_account.get_messages().remove(message)
        # db_account.update_all()

    def tearDown(self):
        self.db_man.close()
