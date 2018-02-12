import re
from json import JSONDecodeError

from iota import Iota, BadApiResponse, ProposedTransaction, Address, TryteString, Tag, Bundle
from iota.crypto.kerl import Kerl
from iota.crypto.kerl.conv import trytes_to_trits, trits_to_trytes
import logging

from messengerapp.utils.exceptions import AppException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IOTAWrapper:
    # The node that we will talk to in order to connect to iota tangle
    # We can host the node our-self
    DEFAULT_NODE_ADDRESS = "http://localhost:14265" #"http://p103.iotaledger.net:14700" #"http://node02.iotatoken.nl:14265"

    # Our channel predefined tag for all messages sent/received
    MESS_TAG = TryteString("MESKAPIOZTAG99999999999999")

    def __init__(self, seed, node_address=None):
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if node_address is None or re.match(url_regex, node_address) is None:
            self.node_address = IOTAWrapper.DEFAULT_NODE_ADDRESS
        else:
            self.node_address = node_address
        self.seed = seed
        self.api = None
        self.node_info = None
        self.address = None

    @staticmethod
    def validate_seed(input_seed, last_digits=3):
        """Make sure only valid seed is enter"""
        seed_chars = list(input_seed.upper())
        allowed_chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ9")
        seed = ""
        i = 0
        if len(input_seed) != 81:
            raise AppException("Invalid Seed", "Seed's length must be of 81-characters length. Please check again")

        for char in seed_chars:
            if char not in allowed_chars:
                char = "9"
                seed += char
            else:
                seed += str(char)
            i += 1

        while len(seed) < 81:
            seed += "9"

        kerl = Kerl()
        trits = trytes_to_trits(seed)
        kerl.absorb(trits)
        trits_out = []
        kerl.squeeze(trits_out)
        checksum = trits_to_trytes(trits_out)[0 - last_digits:]

        return checksum

    def connect_to_iota(self):
        """
        Try to setup connection to Iota tangle
        :return: node_info when success
        """
        try:
            self.api = Iota(self.node_address, self.seed)
            self.node_info = self.api.get_node_info()
            logger.info("Node information: {info}".format(info=self.node_info))
        except JSONDecodeError as e:
            logger.exception("Cannot decode JSON object: {}".format(e))
        except ConnectionError as e:
            logger.exception("Connection error: {e}".format(e=e))
        except BadApiResponse as e:
            logger.exception("IOTA Bad Api Response: {e}".format(e=e))
        else:
            logger.info("Connected.")
            return self.node_info

    def create_new_address(self):
        # Ask Iota API for a new address
        api_response = self.api.get_new_addresses(
            index=6,            # Index of the seed to generate private key
            count=None,         # number of address to generate, default to first unused address
            security_level=1,    # 1/2/3 for 81/162/243 trits level of sec
            checksum=True,
        )
        logger.info(api_response)
        if api_response is not None and type(api_response) is dict \
                and api_response.get("addresses") is not None \
                and len(api_response.get("addresses")) > 0:
            # use the first as our account address
            self.address = api_response["addresses"][0]
        return self.address

    @staticmethod
    def create_new_transaction(address, message, value=0, tag=MESS_TAG):
        return [
            ProposedTransaction(
                address=Address(address),
                value=value,
                message=TryteString.from_string(message),
                tag=Tag(tag)
            )]

    def send_transaction(self, transfer, depth=4, min_weight_magnitude=None):
        try:
            if transfer is None:
                logger.error("No transfer specified!")
                return
            response = self.api.send_transfer(
                depth=depth,
                transfers=transfer,
                min_weight_magnitude=min_weight_magnitude,  # if None, the api will use default number for main-net
            )
        except ConnectionError as e:
            logger.exception("Connection error: {e}".format(e=e))
        except BadApiResponse as e:
            logger.exception("Bad Api Response: {e}".format(e=e))
        else:
            print(response)
            bundle = Bundle(response['bundle'])
            print("Bundle Hash: {}\nFrom Address: {}\nTag:".format(bundle.hash,
                                                                   bundle.transactions[0].address,
                                                                   bundle.transactions[0].tag))

            return response

    def parse_got_bundle(self, bundle):
        pass
