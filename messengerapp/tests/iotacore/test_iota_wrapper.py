import re
from unittest import TestCase

from iota import Address

from messengerapp.iotacore.iotawrapper import IOTAWrapper
from messengerapp.utils.exceptions import AppException


class TestIOTAWrapper(TestCase):

    def test_seed_validation(self):
        raw_seed_too_short = "JABIODLEIRJF9"
        raw_seed_valid = "ZJLUDW9MCJSQKMCESEHJHZKOPZVHNNWKO9IKHUPJMFHXRVVAUNEIQNYOKGYM9DYGMZZNHAIHZYAOTAKAB"
        # seed    9MKUUMIQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLRUJOJC9QEXWCIL9HOUUWMDCAWGFAFSJM
        # address ZJLUDW9MCJSQKMCESEHJHZKOPZVHNNWKO9IKHUPJMFHXRVVAUNEIQNYOKGYM9DYGMZZNHAIHZYAOTAKAB index 7
        self.assertRaises(AppException, IOTAWrapper.validate_seed, raw_seed_too_short)
        self.assertEqual("FX9", IOTAWrapper.validate_seed(raw_seed_valid, 9))

    def test_url_valid(self):
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        self.assertIsNotNone(re.match(url_regex, "http://node02.iotatoken.nl:14265"))


class TestIOTAApi(TestCase):

    def setUp(self):
        seed_valid = "9MKUUMIQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLRUJOJC9QEXWCIL9HOUUWMDCAWGFAFSJM"
        self.iota_wrapper = IOTAWrapper(seed_valid)

    def test_connecting_tangle(self):
        self.iota_wrapper.connect_to_iota()
        response = self.iota_wrapper.create_new_address()
        _address = Address(response, balance=response.balance, key_index=response.key_index, security_level=response.security_level)

        print("Address: {}\nChecksum: {}\nKey Index: {}\nBalance: {}".format(
            _address.address, _address.checksum, _address.key_index, _address.balance))
        # self.assertIsNotNone(self.iota_wrapper.node_info)
        # "Attach" the address to tangle network
        # by sending an empty message transaction
        # transfer = self.iota_wrapper.create_new_transaction(
        #     address=_address,  # a dummy transaction
        #     message="test",
        # )
        # bundle = self.iota_wrapper.send_transaction(transfer)
        # print(bundle)
        pass
