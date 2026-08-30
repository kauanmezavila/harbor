import argparse
import base64
import shutil
from pathlib import Path
from typing import Optional

from ContainerStuff.Obsidian.BaseSystem.crypto import (
    BCB_Descryptography_bytes_passwd,
)


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

MAGENTA = "\033[95m"
CYAN = MAGENTA
BLUE = MAGENTA
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"


def obter_diretorio() -> Path:
    """Read and validate an output directory from CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Analyse a project path."
    )

    parser.add_argument(
        "diretorio",
        nargs="?",
        default=".",
        help="Path to the project directory (default: current directory).",
    )

    args = parser.parse_args()

    caminho = Path(args.diretorio).expanduser().resolve()

    if not caminho.exists():
        parser.error(
            f"[{RED}ERRO{RESET}] The path does not exist: {caminho}!"
        )

    if not caminho.is_dir():
        parser.error(
            f"[{RED}ERRO{RESET}] The path is not a directory: {caminho}!"
        )

    return caminho


def restaurar_container(
    arquivo_bcb: Path,
    senha: str,
    diretorio_saida: Optional[Path] = None,
) -> Path:
    """
    Decrypt a Harbor .bcb file, create a temporary ZIP,
    and extract its contents into a folder with the same
    name as the ZIP.
    """

    arquivo_bcb = Path(arquivo_bcb).expanduser().resolve()

    if diretorio_saida is None:
        diretorio_saida = obter_diretorio()
    else:
        diretorio_saida = Path(diretorio_saida).expanduser().resolve()

    if not arquivo_bcb.exists():
        raise FileNotFoundError(
            f"[{RED}ERRO{RESET}] Encrypted file not found: "
            f"{arquivo_bcb}"
        )

    if not arquivo_bcb.is_file():
        raise ValueError(
            f"[{RED}ERRO{RESET}] Encrypted path is not a file: "
            f"{arquivo_bcb}"
        )

    if not senha:
        raise ValueError(
            f"[{RED}ERRO{RESET}] A password is required."
        )

    with arquivo_bcb.open("r", encoding="utf-8") as arquivo:
        texto_criptografado = arquivo.read()

    texto_base64 = BCB_Descryptography_bytes_passwd(
        texto_criptografado,
        senha,
    )

    try:
        container_bytes = base64.b64decode(
            texto_base64,
            validate=True,
        )
    except Exception as erro:
        raise ValueError(
            f"[{RED}ERRO{RESET}] Could not decode decrypted data "
            "as Base64. The password may be incorrect or the "
            "file may be corrupted."
        ) from erro


    diretorio_saida.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo_zip = diretorio_saida / f"{arquivo_bcb.stem}.zip"

    with arquivo_zip.open("wb") as arquivo:
        arquivo.write(container_bytes)

    pasta_extracao = diretorio_saida / arquivo_zip.stem

    pasta_extracao.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        shutil.unpack_archive(
            str(arquivo_zip),
            str(pasta_extracao),
            format="zip",
        )

    except Exception as erro:
        arquivo_zip.unlink(missing_ok=True)

        try:
            pasta_extracao.rmdir()
        except OSError:
            pass

        raise ValueError(
            f"[{RED}ERRO{RESET}] The decrypted data is not "
            "a valid ZIP archive."
        ) from erro

    arquivo_zip.unlink(missing_ok=True)

    return pasta_extracao