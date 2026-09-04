from pathlib import Path
from tempfile import TemporaryDirectory

from ContainerStuff.WrapperStuff.hashflux import extract_harb, find_container_root, hash_folder

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


def verify(container):
    """
    Verify the complete hash tree without rewriting hashes.

    Checks:
    1. The current root hash against the saved root hash.
    2. Every .hash.txt against the current hash of its folder.
    3. Which folders have compatible/incompatible hashes.
    4. Repeated saved hash values.
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

    if container.is_file():
        if container.suffix.lower() != ".harb":
            raise ValueError(
                f"\n[{RED}ERROR{RESET}] "
                f"Expected a .harb file: {container}"
            )

        print(
            f"\n[{BOLD}{CYAN}VERIFY{RESET}] "
            f".harb file: {container}"
        )

        with TemporaryDirectory() as temp_dir:
            extract_harb(container, temp_dir)
            return verify(
                find_container_root(temp_dir)
            )

    if not container.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERROR{RESET}] "
            "Container path is not a directory: "
            f"{container}"
        )

    # ---------------------------------------------------------
    # 1. Find every saved hash.
    # ---------------------------------------------------------

    hash_files = sorted(
        container.rglob(HASH_FILE)
    )

    if not hash_files:
        print(
            f"[{RED}VERIFY{RESET}] "
            "No .hash.txt files were found."
        )

        return {
            "root_integrity": False,
            "hashes_found": 0,
            "compatible_hashes": 0,
            "incompatible_hashes": 0,
            "repeated_hashes": 0,
            "unique_hashes": 0,
            "results": [],
        }

    # ---------------------------------------------------------
    # 2. Calculate the current root hash.
    #
    # hash_folder ignores every .hash.txt, so this represents
    # the current content of the entire container.
    # ---------------------------------------------------------

    current_root_hash = hash_folder(
        container,
        write=False,
    )

    # ---------------------------------------------------------
    # 3. Read the saved root hash.
    # ---------------------------------------------------------

    root_hash_file = (
        container / HASH_FILE
    )

    saved_root_hash = None

    if root_hash_file.is_file():
        saved_root_hash = (
            root_hash_file
            .read_text(encoding="utf-8")
            .strip()
        )

    root_integrity = (
        saved_root_hash is not None
        and saved_root_hash == current_root_hash
    )

    # ---------------------------------------------------------
    # 4. Verify every .hash.txt against its own folder.
    # ---------------------------------------------------------

    results = []

    for hash_file in hash_files:
        folder = hash_file.parent

        saved_hash = (
            hash_file
            .read_text(encoding="utf-8")
            .strip()
        )

        current_hash = hash_folder(
            folder,
            write=False,
        )

        compatible = (
            saved_hash == current_hash
        )

        try:
            relative_path = (
                hash_file.relative_to(container)
            )
        except ValueError:
            relative_path = hash_file

        results.append(
            {
                "hash_file": hash_file,
                "folder": folder,
                "relative_path": relative_path,
                "saved_hash": saved_hash,
                "current_hash": current_hash,
                "compatible": compatible,
            }
        )

    # ---------------------------------------------------------
    # 5. Statistics.
    # ---------------------------------------------------------

    compatible_hashes = sum(
        result["compatible"]
        for result in results
    )

    incompatible_hashes = (
        len(results)
        - compatible_hashes
    )

    values = [
        result["saved_hash"]
        for result in results
    ]

    unique_hashes = len(set(values))

    repeated_hashes = (
        len(values)
        - unique_hashes
    )

    # ---------------------------------------------------------
    # 6. Display root verification.
    # ---------------------------------------------------------

    print()
    print(
        f"[{BOLD}{CYAN}VERIFY{RESET}] "
        f"Container: {container}"
    )

    print()

    print(
        f"      Root hash saved   : "
        f"{YELLOW}{saved_root_hash}{RESET}"
    )

    print(
        f"      Root hash current : "
        f"{YELLOW}{current_root_hash}{RESET}"
    )

    if root_integrity:
        print(
            f"      Root integrity    : "
            f"{GREEN}VALID{RESET}"
        )
    else:
        print(
            f"      Root integrity    : "
            f"{RED}INVALID{RESET}"
        )

    # ---------------------------------------------------------
    # 7. Display each .hash.txt verification.
    # ---------------------------------------------------------

    print()

    for result in results:
        path = result["relative_path"]

        if result["compatible"]:
            status = f"{GREEN}VALID{RESET}"
        else:
            status = f"{RED}INVALID{RESET}"

        print(
            f"      [{status}] "
            f"{path}"
        )

        if not result["compatible"]:
            print(
                f"          Saved : "
                f"{result['saved_hash']}"
            )

            print(
                f"          Actual: "
                f"{result['current_hash']}"
            )

    # ---------------------------------------------------------
    # 8. Summary.
    # ---------------------------------------------------------

    print()

    print(
        f"      Hashes on project     : "
        f"{len(hash_files)}"
    )

    print(
        f"      Compatible hashes     : "
        f"{GREEN}{compatible_hashes}{RESET}"
    )

    print(
        f"      Incompatible hashes   : "
        f"{RED}{incompatible_hashes}{RESET}"
    )

    print(
        f"      Repeated saved hashes : "
        f"{repeated_hashes}"
    )

    print(
        f"      Unique saved hashes   : "
        f"{unique_hashes}"
    )

    print()

    # ---------------------------------------------------------
    # 9. Final integrity conclusion.
    # ---------------------------------------------------------

    project_integrity = (
        root_integrity
        and incompatible_hashes == 0
    )

    if project_integrity:
        print(
            f"[{GREEN} OK {RESET}] "
            "Container integrity verified."
        )
    else:
        print(
            f"[{RED}ERROR{RESET}] "
            "Container integrity check failed."
        )

    print()

    return {
        "saved_root_hash": saved_root_hash,
        "current_root_hash": current_root_hash,
        "root_integrity": root_integrity,
        "project_integrity": project_integrity,
        "hashes_found": len(hash_files),
        "compatible_hashes": compatible_hashes,
        "incompatible_hashes": incompatible_hashes,
        "repeated_hashes": repeated_hashes,
        "unique_hashes": unique_hashes,
        "results": results,
    }
