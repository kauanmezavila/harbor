from crypto import (
    ALFABETO,
    BCB_Cryptography_bytes_passwd,
    BCB_Descryptography_bytes_passwd,
    BCB_bytes_text,
    chave_valida,
)


def main_bcb_crypt_flux_v1(path, senha):
    """Read a file and return its encrypted Base64 payload."""
    if chave_valida(senha, ALFABETO) is True:
        file_bytes = BCB_bytes_text(path)
        cripto_final = BCB_Cryptography_bytes_passwd(file_bytes, senha)
        return cripto_final

    return


def main_bcb_decrypt_flux_v1(path, senha):
    """Read a file and return its decrypted Base64 payload."""
    if chave_valida(senha, ALFABETO) is True:
        file_bytes = BCB_bytes_text(path)
        decripto_final = BCB_Descryptography_bytes_passwd(file_bytes, senha)
        return decripto_final

    return
