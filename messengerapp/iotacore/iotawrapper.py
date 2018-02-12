import base64
import re
from json import JSONDecodeError

from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
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
    MESS_TAG = "MESKAPIOZTAG99999999999999"

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
        self.node_info = None
        self.address = None
        self.api = Iota(self.node_address, self.seed)

    def get_node_info(self):
        """
        Try to setup connection to Iota tangle
        :return: node_info when success
        """
        try:
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
            index=6,             # Index of the seed to generate private key
            count=None,          # number of address to generate, default to first unused address
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

    @staticmethod
    def convert_string_to_trytes(plain_text):
        return TryteString.from_string(plain_text)

    @staticmethod
    def get_tags(raw_tag):
        tryte_tag = TryteString(raw_tag)
        tryte_tag += '9' * (27 - len(tryte_tag))
        return Tag(tryte_tag)

    @staticmethod
    def create_new_transaction(address, message, value=0, tag=MESS_TAG):
        return [
            ProposedTransaction(
                address=Address(address),
                value=value,
                message=TryteString.from_string(message),
                tag=IOTAWrapper.get_tags(tag)
            )]

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

    @staticmethod
    def generate_rsa_key_pair():
        """ Create new RSA key-pair to encrypt messages

        :return: a tuple of PRIAVE-PUBLIC key pair encoded with base64
        """
        # RSA modulus length must be a multiple of 256 and >= 1024
        modulus_length = 256 * 4  # use larger value in production
        privatekey = RSA.generate(modulus_length, Random.new().read)
        publickey = privatekey.publickey()

        print(base64.b64encode(privatekey.exportKey(format="DER")).decode())
        print(base64.b64encode(publickey.exportKey(format="DER")).decode())
        return base64.b64encode(privatekey.exportKey()), base64.b64encode(publickey.exportKey())

    @staticmethod
    def aes_encryption(raw_message):
        """
        Symmetric encryption of raw message
        return the cipher text and aes key to decrypt the cipher text
        :return: tuple of cipher_text, aes_key
        """
        # Generate a random AES Key and iv for encryption
        aes_key = Random.new().read(32)
        iv = Random.new().read(AES.block_size)
        aes_cipher = AES.new(aes_key, AES.MODE_CFB, iv)
        cryptic_message = base64.b64encode(iv + aes_cipher.encrypt(raw_message.encode(encoding='utf-8')))

        return cryptic_message, aes_key

    @staticmethod
    def aes_decryption(cipher_text, aes_key):
        """
        Symmetric decryption of cipher text using the aes key
        :return: raw message
        """
        enc = base64.b64decode(cipher_text)
        iv = enc[:16]
        aes_cipher = AES.new(aes_key, AES.MODE_CFB, iv)
        raw_message = aes_cipher.decrypt(enc[16:]).decode('utf-8')

        return raw_message

    @staticmethod
    def rsa_encryption(raw_message, public_key):
        """
        Asymmetric encryption of given message using the public key
        :return: the encrypted message
        """
        encryptor = PKCS1_OAEP.new(RSA.import_key(public_key))
        encrypted_msg = base64.b64encode(encryptor.encrypt(raw_message))

        return encrypted_msg

    @staticmethod
    def rsa_decryption(encrypted_msg, private_key):
        """
        Asymmetric decryption of encrypted message using the private key
        :return: the raw_message
        """
        decryptor = PKCS1_OAEP.new(RSA.import_key(private_key))
        decrypted_msg = decryptor.decrypt(base64.b64decode(encrypted_msg))

        return decrypted_msg

    @staticmethod
    def message_encryption(raw_message, public_key):
        """
        Encrypt raw message using aes encryption, then encrypt the aes key using rsa pub/pri key
        :return: the encrypted message and encrypted key
        """
        cipher_text, aes_key = IOTAWrapper.aes_encryption(raw_message)
        aes_cipher = IOTAWrapper.rsa_encryption(aes_key, public_key)
        return cipher_text, aes_cipher

    @staticmethod
    def message_decryption(cipher_text, aes_cipher, private_key):
        """
        Decrypt the encrypted message by first decrypt the aes cipher key using rsa private key
        :return: return the original message
        """
        aes_key = IOTAWrapper.rsa_decryption(aes_cipher, private_key)
        raw_message = IOTAWrapper.aes_decryption(cipher_text, aes_key)
        return raw_message
