import hashlib
from pathlib import Path

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


def hash_file(file_path):
    """Return the SHA-256 hash for one file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            sha256.update(block)

    return sha256.hexdigest()


def hash_folder(folder, write=True):
    """
    Calculate a recursive SHA-256 hash for a folder.

    .hash.txt files are always ignored.

    The hash of a folder depends on:
    - the names and hashes of its files;
    - the names and hashes of its subdirectories.

    If write=True, the resulting hash is written to
    <folder>/.hash.txt.
    """
    folder = Path(folder)
    items = []

    for item in sorted(
        folder.iterdir(),
        key=lambda x: x.name,
    ):
        # Never include hash files in the hash calculation.
        if item.name == HASH_FILE:
            continue

        if item.is_file():
            item_hash = hash_file(item)

            items.append(
                f"FILE:{item.name}:{item_hash}"
            )

        elif item.is_dir():
            item_hash = hash_folder(
                item,
                write=write,
            )

            items.append(
                f"DIR:{item.name}:{item_hash}"
            )

    data = "\n".join(items).encode("utf-8")

    current_folder_hash = hashlib.sha256(
        data
    ).hexdigest()

    if write:
        hash_path = folder / HASH_FILE

        with open(
            hash_path,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(current_folder_hash)

    return current_folder_hash


def update_hash(container):
    """
    Recalculate and rewrite the complete hash tree.
    """

    container = (
        Path(container)
        .expanduser()
        .resolve()
    )

    if not container.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERROR{RESET}] "
            f"Container not found: {container}"
        )

    if not container.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERROR{RESET}] "
            f"Container path is not a directory: {container}"
        )

    print(
        f"\n[{YELLOW}UPDATE HASH{RESET}] "
        "Updating integrity hashes..."
    )

    root_hash = hash_folder(
        container,
        write=True,
    )

    print(
        f"[{GREEN} OK {RESET}] "
        "Integrity hashes updated."
    )

    print(
        f"      Root hash: "
        f"{YELLOW}{root_hash}{RESET}\n"
    )

    return root_hash
