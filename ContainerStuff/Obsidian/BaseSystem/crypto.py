import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


ALFABETO = ""
AES_PREFIX = "HBAES1:"
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
KDF_ITERATIONS = 390000


def chave_valida(chave, alfabeto=None):
    return bool(chave)


def _key(chave, salt):
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=KDF_ITERATIONS,
    ).derive(chave.encode("utf-8"))


def BCB_bytes_text(path):
    with open(path, "rb") as arquivo:
        return base64.b64encode(arquivo.read()).decode("ascii")


def BCB_text_bytes(path):
    with open(path, "r", encoding="utf-8") as arquivo:
        return base64.b64decode(arquivo.read())


def BCB_Cryptography_bytes_passwd(texto, chave, iv=None):
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    encrypted = AESGCM(_key(chave, salt)).encrypt(
        nonce,
        texto.encode("utf-8"),
        None,
    )
    payload = base64.b64encode(salt + nonce + encrypted).decode("ascii")
    return AES_PREFIX + payload


def BCB_Descryptography_bytes_passwd(texto, chave, iv=None):
    if not texto.startswith(AES_PREFIX):
        raise ValueError("Unsupported encrypted file format.")

    payload = base64.b64decode(texto[len(AES_PREFIX):])
    salt = payload[:SALT_SIZE]
    nonce = payload[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    encrypted = payload[SALT_SIZE + NONCE_SIZE:]

    decrypted = AESGCM(_key(chave, salt)).decrypt(nonce, encrypted, None)
    return decrypted.decode("utf-8")