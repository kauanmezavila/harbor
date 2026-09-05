import os
import shutil
from pathlib import Path

import pathspec

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


def create_container(container_name: str, directory: Path) -> Path:
    """Create the Harbor container with Code and Info directories."""
    container_path = directory.parent / container_name

    if container_path.exists():
        print(f"\n[{YELLOW}INFO{RESET}] Container already exists:")
        print(f"  {container_path}")

        answer = input("\n[!] Want to overwrite? [y/N]: ").strip().lower()

        if answer != "y":
            print(f"[{YELLOW}INFO{RESET}] Operation cancelled.")
            raise SystemExit(0)

        print(f"[{YELLOW}INFO{RESET}] Removing old container...")

        if container_path.is_dir():
            shutil.rmtree(container_path)
        else:
            container_path.unlink()

    container_path.mkdir(parents=True, exist_ok=True)
    (container_path / "Code").mkdir(exist_ok=True)
    (container_path / "Info").mkdir(exist_ok=True)

    print(f"[{GREEN} OK {RESET}] Container created: {container_path}")

    return container_path


def load_ignore(
    directory: Path,
    default: Path | None = None,
) -> pathspec.PathSpec | None:
    """Choose and load .harbignore rules for the copy step."""
    project_ignore = directory / ".harbignore"

    default_ignore = (
        Path(default)
        if default is not None
        else Path(__file__).resolve().parent / ".harbignore"
    )

    if project_ignore.is_file():
        print(f"\n[{CYAN}IGNORE{RESET}] Project .harbignore found:")
        print(f"  {project_ignore}")

        answer = input("\n[?] Use project .harbignore? [Y/n]: ").strip().lower()

        if answer in ("", "y", "yes"):
            ignore_path = project_ignore

        elif default_ignore.is_file():
            answer = (
                input("\n[?] Use default Harbor .harbignore? [Y/n]: ").strip().lower()
            )

            if answer in ("", "y", "yes"):
                ignore_path = default_ignore

            else:
                print(f"[{YELLOW}INFO{RESET}] No ignore file will be used.")
                return None

        else:
            print(f"[{YELLOW}INFO{RESET}] No default .harbignore found.")

            answer = (
                input("\n[?] Use default Harbor .harbignore? [Y/n]: ").strip().lower()
            )

            if answer in ("", "y", "yes"):
                ignore_path = default_ignore

            else:
                print(f"[{YELLOW}INFO{RESET}] No ignore file will be used.")
                return None

    else:
        if not default_ignore.is_file():
            print(f"[{YELLOW}INFO{RESET}] No .harbignore found.")
            return None

        print(f"\n[{CYAN}IGNORE{RESET}] Default Harbor .harbignore found:")
        print(f"  {default_ignore}")

        answer = input("\n[?] Use default Harbor .harbignore? [Y/n]: ").strip().lower()

        if answer in ("", "y", "yes"):
            ignore_path = default_ignore

        else:
            print(f"[{YELLOW}INFO{RESET}] No ignore file will be used.")
            return None

    with ignore_path.open("r", encoding="utf-8") as file:
        lines = [
            line.strip()
            for line in file
            if line.strip() and not line.lstrip().startswith("#")
        ]

    if not lines:
        print(f"[{YELLOW}INFO{RESET}] Ignore file is empty.")
        return None

    print(f"[{GREEN} OK {RESET}] Using ignore file: {ignore_path}")

    return pathspec.PathSpec.from_lines(
        "gitwildmatch",
        lines,
    )


def copy_project(source: Path, destination: Path) -> bool:
    """Copy project files into Code and root metadata files into Info."""
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()

    info_files = {"header.json", "tree.json", ".harbignore", ".harbinstall"}

    if not source.exists():
        raise FileNotFoundError(f"\n[{RED}ERROR{RESET}] Origin not found: {source}")

    if not source.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERROR{RESET}] The origin is not a directory: {source}"
        )

    if destination == source:
        raise ValueError(f"\n[{RED}ERROR{RESET}] The destination cannot be the origin.")

    try:
        destination.relative_to(source)

    except ValueError:
        pass

    else:
        raise ValueError(
            f"\n[{RED}ERROR{RESET}] "
            f"The destination cannot be inside "
            f"the origin: {destination}"
        )

    destination.mkdir(parents=True, exist_ok=True)

    info_destination = destination.parent / "Info"
    info_destination.mkdir(parents=True, exist_ok=True)

    ignore = load_ignore(source)

    git_ask_use = (
        input(
            "\nWant to include .git on the container? "
            "(I don't recommend including it...) [y/N]: "
        )
        .strip()
        .lower()
    )

    include_git = git_ask_use == "y"

    print()
    print(f"[{BOLD} MAKE {RESET}] {source}")
    print("     V")
    print(f"[{BOLD} CODE {RESET}] {destination}")
    print(f"[{BOLD} INFO {RESET}] {info_destination}")
    print()

    copied = 0
    ignored = 0
    infos = 0

    for root, folders, files in os.walk(source):
        root = Path(root)
        relative_root = root.relative_to(source)

        valid_folders = []

        for folder in folders:
            path = root / folder

            relative_path = path.relative_to(source).as_posix()

            ignore_path = relative_path + "/"

            if folder == ".git":
                if not include_git:
                    ignored += 1
                    print(f"[{YELLOW} IGNORE {RESET}] {ignore_path}")
                    continue

                valid_folders.append(folder)
                continue

            if ignore and ignore.match_file(ignore_path):
                ignored += 1

                print(f"[{YELLOW} IGNORE {RESET}] {ignore_path}")

                continue

            valid_folders.append(folder)

        # Update os.walk in place so ignored folders are not visited.
        folders[:] = valid_folders

        destination_root = destination / relative_root
        destination_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        for file_name in files:
            source_file = root / file_name

            relative_file = source_file.relative_to(source)

            relative_file_str = relative_file.as_posix()

            if ignore and ignore.match_file(relative_file_str):
                ignored += 1

                print(f"[{YELLOW} IGNORE {RESET}] {relative_file_str}")

                continue

            if relative_file.parent == Path(".") and file_name in info_files:
                shutil.copy2(
                    source_file,
                    info_destination / file_name,
                )

                infos += 1

                print(f"[{CYAN}  INFO  {RESET}] {relative_file_str}")

                continue

            destination_file = destination / relative_file

            destination_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source_file,
                destination_file,
            )

            copied += 1

            print(f"[{GREEN}  CODE  {RESET}] {relative_file_str}")

    print()
    print(f"[{GREEN} OK {RESET}] Project copied successfully.")
    print(f"      Files copied : {copied}")
    print(f"      Info files   : {infos}")
    print(f"      Items ignored: {ignored}")
    print(f"      Code         : {destination}")
    print(f"      Info         : {info_destination}")
    print()

    return True
