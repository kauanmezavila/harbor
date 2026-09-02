from ContainerStuff.Obsidian.BaseSystem.crypto import (
    ALPHABET,
    BCB_Cryptography_bytes_passwd,
    BCB_Descryptography_bytes_passwd,
    BCB_bytes_text,
    valid_key,
)


def main_bcb_crypt_flux_v1(path, password):
    """Read a file and return its encrypted Base64 payload."""
    if valid_key(password, ALPHABET) is True:
        file_bytes = BCB_bytes_text(path)
        encrypted_content = BCB_Cryptography_bytes_passwd(file_bytes, password)
        return encrypted_content

    return


def main_bcb_decrypt_flux_v1(path, password):
    """Read a file and return its decrypted Base64 payload."""
    if valid_key(password, ALPHABET) is True:
        file_bytes = BCB_bytes_text(path)
        decrypted_content = BCB_Descryptography_bytes_passwd(file_bytes, password)
        return decrypted_content

    return
