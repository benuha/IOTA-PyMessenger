import base64

from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA


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


def aes_decryption(cipher_text, aes_key):
    """
    Symmetric decryption of cipher text using the aes key
    :return: raw message
    """
    enc = base64.b64decode(cipher_text)
    iv = enc[:16]
    from Crypto.Cipher import AES
    aes_cipher = AES.new(aes_key, AES.MODE_CFB, iv)
    raw_message = aes_cipher.decrypt(enc[16:]).decode('utf-8')

    return raw_message


def rsa_encryption(raw_message, public_key):
    """
    Asymmetric encryption of given message using the public key
    :return: the encrypted message
    """
    encryptor = PKCS1_OAEP.new(RSA.import_key(public_key))
    encrypted_msg = base64.b64encode(encryptor.encrypt(raw_message))

    return encrypted_msg


def rsa_decryption(encrypted_msg, private_key):
    """
    Asymmetric decryption of encrypted message using the private key
    :return: the raw_message
    """
    decryptor = PKCS1_OAEP.new(RSA.import_key(private_key))
    decrypted_msg = decryptor.decrypt(base64.b64decode(encrypted_msg))

    return decrypted_msg


def message_encryption(raw_message, public_key):
    """
    Encrypt raw message using aes encryption, then encrypt the aes key using rsa pub/pri key
    :return: the encrypted message and encrypted key
    """
    cipher_text, aes_key = aes_encryption(raw_message)
    aes_cipher = rsa_encryption(aes_key, public_key)
    return cipher_text, aes_cipher


def message_decryption(cipher_text, aes_cipher, private_key):
    """
    Decrypt the encrypted message by first decrypt the aes cipher key using rsa private key
    :return: return the original message
    """
    aes_key = rsa_decryption(aes_cipher, private_key)
    raw_message = aes_decryption(cipher_text, aes_key)
    return raw_message
