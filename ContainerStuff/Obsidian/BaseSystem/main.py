from ContainerStuff.Obsidian.BaseSystem.crypto import (
    ALPHABET,
    BCB_bytes_text,
    BCB_Cryptography_bytes_passwd,
    BCB_Descryptography_bytes_passwd,
    valid_key,
)


def main_bcb_crypt_flux_v1(path, password):
    """Read a file and return its encrypted Base64 payload."""
    if valid_key(password, ALPHABET) is True:
        file_bytes = BCB_bytes_text(path)
        return BCB_Cryptography_bytes_passwd(file_bytes, password)

    return None


def main_bcb_decrypt_flux_v1(path, password):
    """Read an encrypted file and return its decrypted Base64 payload."""
    if valid_key(password, ALPHABET) is True:
        with open(path, encoding="utf-8") as file:
            encrypted_text = file.read()

        return BCB_Descryptography_bytes_passwd(encrypted_text, password)

    return None
