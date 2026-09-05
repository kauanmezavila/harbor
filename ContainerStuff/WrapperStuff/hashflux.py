import hashlib
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

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


def extract_harb(harb_file, destination):
    """Extract a .harb zip archive without allowing path traversal."""
    destination = Path(destination).resolve()

    with zipfile.ZipFile(harb_file) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()

            if destination != target and destination not in target.parents:
                raise ValueError(
                    f"\n[{RED}ERROR{RESET}] Unsafe path inside .harb: {member.filename}"
                )

        archive.extractall(destination)


def find_container_root(directory):
    """Return the extracted Harbor folder when the archive has one root."""
    roots = [path for path in Path(directory).iterdir() if path.is_dir()]

    if len(roots) == 1:
        return roots[0]

    raise ValueError(
        f"\n[{RED}ERROR{RESET}] .harb archive must contain one container root folder."
    )


def write_harb(container, harb_file):
    """Write a Harbor folder back to a .harb archive."""
    container = Path(container)
    harb_file = Path(harb_file)
    temp_harb = harb_file.with_name(f"{harb_file.name}.tmp")

    with zipfile.ZipFile(
        temp_harb,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for path in sorted(container.rglob("*")):
            if path.is_file():
                archive.write(
                    path,
                    path.relative_to(container.parent),
                )

    temp_harb.replace(harb_file)


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

            items.append(f"FILE:{item.name}:{item_hash}")

        elif item.is_dir():
            item_hash = hash_folder(
                item,
                write=write,
            )

            items.append(f"DIR:{item.name}:{item_hash}")

    data = "\n".join(items).encode("utf-8")

    current_folder_hash = hashlib.sha256(data).hexdigest()

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

    Accepts an extracted Harbor directory or a compressed .harb file.
    """

    container = Path(container).expanduser().resolve()

    if not container.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERROR{RESET}] Container not found: {container}"
        )

    if container.is_file():
        if container.suffix.lower() != ".harb":
            raise ValueError(
                f"\n[{RED}ERROR{RESET}] Expected a .harb file: {container}"
            )

        print(f"\n[{YELLOW}UPDATE HASH{RESET}] Updating .harb integrity hashes...")

        with TemporaryDirectory() as temp_dir:
            extract_harb(container, temp_dir)
            extracted = find_container_root(temp_dir)
            root_hash = hash_folder(
                extracted,
                write=True,
            )
            write_harb(extracted, container)

        print(f"[{GREEN} OK {RESET}] .harb integrity hashes updated.")

        print(f"      Root hash: {YELLOW}{root_hash}{RESET}\n")

        return root_hash

    if not container.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERROR{RESET}] Container path is not a directory: {container}"
        )

    print(f"\n[{YELLOW}UPDATE HASH{RESET}] Updating integrity hashes...")

    root_hash = hash_folder(
        container,
        write=True,
    )

    print(f"[{GREEN} OK {RESET}] Integrity hashes updated.")

    print(f"      Root hash: {YELLOW}{root_hash}{RESET}\n")

    return root_hash
