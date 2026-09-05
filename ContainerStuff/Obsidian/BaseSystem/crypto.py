import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ALPHABET = ""
AES_PREFIX = "HBAES1:"
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
KDF_ITERATIONS = 390000


def valid_key(key, alphabet=None):
    return bool(key)


def _key(key, salt):
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=KDF_ITERATIONS,
    ).derive(key.encode("utf-8"))


def BCB_bytes_text(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode("ascii")


def BCB_text_bytes(path):
    with open(path, "r", encoding="utf-8") as file:
        return base64.b64decode(file.read())


def BCB_Cryptography_bytes_passwd(text, key, iv=None):
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    encrypted = AESGCM(_key(key, salt)).encrypt(
        nonce,
        text.encode("utf-8"),
        None,
    )
    payload = base64.b64encode(salt + nonce + encrypted).decode("ascii")
    return AES_PREFIX + payload


def BCB_Descryptography_bytes_passwd(text, key, iv=None):
    if not text.startswith(AES_PREFIX):
        raise ValueError("Unsupported encrypted file format.")

    payload = base64.b64decode(text[len(AES_PREFIX) :])
    salt = payload[:SALT_SIZE]
    nonce = payload[SALT_SIZE : SALT_SIZE + NONCE_SIZE]
    encrypted = payload[SALT_SIZE + NONCE_SIZE :]

    decrypted = AESGCM(_key(key, salt)).decrypt(nonce, encrypted, None)
    return decrypted.decode("utf-8")
