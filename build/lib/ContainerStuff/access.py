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


def get_directory() -> Path:
    """Read and validate an output directory from CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Analyse a project path."
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Path to the project directory (default: current directory).",
    )

    args = parser.parse_args()

    path = Path(args.directory).expanduser().resolve()

    if not path.exists():
        parser.error(f"[{RED}ERROR{RESET}] The path does not exist: {path}!")

    if not path.is_dir():
        parser.error(f"[{RED}ERROR{RESET}] The path is not a directory: {path}!")

    return path


def restore_container(
    bcb_file: Path,
    password: str,
    output_dir: Optional[Path] = None,
) -> Path:
    """
    Decrypt a Harbor .bcb file, create a temporary ZIP,
    and extract its contents into a folder with the same
    name as the ZIP.
    """

    bcb_file = Path(bcb_file).expanduser().resolve()

    if output_dir is None:
        output_dir = get_directory()
    else:
        output_dir = Path(output_dir).expanduser().resolve()

    if not bcb_file.exists():
        raise FileNotFoundError(
            f"[{RED}ERROR{RESET}] Encrypted file not found: {bcb_file}"
        )

    if not bcb_file.is_file():
        raise ValueError(
            f"[{RED}ERROR{RESET}] Encrypted path is not a file: {bcb_file}"
        )

    if not password:
        raise ValueError(f"[{RED}ERROR{RESET}] A password is required.")

    with bcb_file.open("r", encoding="utf-8") as file:
        encrypted_text = file.read()

    base64_text = BCB_Descryptography_bytes_passwd(
        encrypted_text,
        password,
    )

    try:
        container_bytes = base64.b64decode(
            base64_text,
            validate=True,
        )
    except Exception as error:
        raise ValueError(
            f"[{RED}ERROR{RESET}] Could not decode decrypted data "
            "as Base64. The password may be incorrect or the "
            "file may be corrupted."
        ) from error

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    zip_file = output_dir / f"{bcb_file.stem}.zip"

    with zip_file.open("wb") as file:
        file.write(container_bytes)

    extraction_dir = output_dir / zip_file.stem

    extraction_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        shutil.unpack_archive(
            str(zip_file),
            str(extraction_dir),
            format="zip",
        )

    except Exception as error:
        zip_file.unlink(missing_ok=True)

        try:
            extraction_dir.rmdir()
        except OSError:
            pass

        raise ValueError(
            f"[{RED}ERROR{RESET}] The decrypted data is not "
            "a valid ZIP archive."
        ) from error

    zip_file.unlink(missing_ok=True)

    return extraction_dir
