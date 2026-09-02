import argparse
import shutil
from pathlib import Path
from typing import Optional

from ContainerStuff.header import header
from ContainerStuff.Obsidian.BaseSystem.crypto import (
    BCB_Cryptography_bytes_passwd,
    BCB_bytes_text,
)
from ContainerStuff.WrapperStuff.containerflux import copy_project, create_container
from ContainerStuff.WrapperStuff.hashflux import hash_folder


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

HASH_FILE = ".hash.txt"


def get_directory() -> Path:
    """Read and validate the project directory from CLI arguments."""
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

    print(f"[{GREEN} OK {RESET}] Project found: [{path}]")

    return path


def main_wrapper(path: Optional[Path] = None) -> None:
    """Create a Harbor container for a project directory."""
    project_dir = (
        path
        if path
        else get_directory()
    )

    project_dir = (
        Path(project_dir)
        .expanduser()
        .resolve()
    )

    if not project_dir.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERROR{RESET}] "
            f"Project directory not found: {project_dir}"
        )

    if not project_dir.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERROR{RESET}] "
            f"Project path is not a directory: {project_dir}"
        )

    project_name = header(project_dir)

    if not project_name:
        raise ValueError(
            f"\n[{RED}ERROR{RESET}] "
            "Could not determine the project name."
        )

    container = create_container(
        project_name,
        project_dir,
    )

    code_path = container / "Code"

    copy_project(
        project_dir,
        code_path,
    )

    # Creates the complete recursive hash tree.
    hash_code = hash_folder(container)

    create_encrypted = input(
        "\n[?] Create encrypted copy of the container? [Y/n]: "
    )

    create_encrypted = create_encrypted.strip().lower()

    if create_encrypted in ("", "y", "yes"):
        password = input(
            "\n[?] Enter a password for encryption: "
        ).strip()

        if not password:
            print(
                f"[{YELLOW}INFO{RESET}] "
                "No password provided. Skipping encryption."
            )
            return

        zip_file = (
            container.parent
            / f"{project_name}.zip"
        )

        shutil.make_archive(
            str(zip_file.with_suffix("")),
            "zip",
            container,
        )

        container_bytes = BCB_bytes_text(
            zip_file
        )

        output_file = (
            container.parent
            / f"{project_name}_encrypted.bcb"
        )

        encrypted_content = (
            BCB_Cryptography_bytes_passwd(
                container_bytes,
                password,
            )
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(encrypted_content)

        zip_file.unlink()

        print(
            f"[{GREEN} OK {RESET}] "
            f"Encrypted copy created: {output_file}"
        )

    print(
        f"\n[{GREEN} OK {RESET}] "
        "Container creation completed successfully on: "
        f"\n>>>  {container}"
        f"\n\nHash: {YELLOW}{hash_code}{RESET}\n"
    )


if __name__ == "__main__":
    main_wrapper()
