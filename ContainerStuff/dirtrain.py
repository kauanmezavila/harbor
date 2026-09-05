import json
import os
from pathlib import Path

import pathspec

from ContainerStuff.stack import STACKS

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


def c(text: str, color: str) -> str:
    """Wrap text in an ANSI color sequence."""
    return f"{color}{text}{RESET}"


def title(text: str):
    """Print a compact section title."""
    width = 64

    print()
    print(c("//" + "=" * width + r"\\", CYAN))
    print(c("||", CYAN) + f"  {text:<{width - 2}}" + c("||", CYAN))
    print(c(r"\\" + "=" * width + "//", CYAN))
    print()


def line():
    """Print a visual divider."""
    print(c("--" * 64, GRAY))


class StackDetector:
    """Detect project stacks from known file, extension, and folder names."""

    def __init__(self):
        self.detected = {}

    def detect(self, name: str, is_file: bool):
        if is_file and name in STACKS.get("files", {}):
            return STACKS["files"][name]["stack"]

        if is_file:
            ext = Path(name).suffix
            if ext in STACKS.get("extensions", {}):
                return STACKS["extensions"][ext]["stack"]

        if not is_file and name in STACKS.get("folders", {}):
            return STACKS["folders"][name]

        return None

    def add_stack(self, stack: str, path: str):
        self.detected.setdefault(stack, []).append(path)


def find_runtime(stack: str):
    """Find the first runtime declared for a detected stack."""
    for category in ("extensions", "files"):
        for data in STACKS.get(category, {}).values():
            if not isinstance(data, dict):
                continue

            if data.get("stack") != stack:
                continue

            if "runtime" in data:
                return data["runtime"]

            if data.get("required"):
                return data["required"][0]

    return None


def load_ignore(directory: str):
    """Load .harbignore rules from a scanned directory."""
    ignore_path = os.path.join(directory, ".harbignore")

    if not os.path.isfile(ignore_path):
        return None

    with open(ignore_path, "r", encoding="utf-8") as f:
        lines = [
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        ]

    if not lines:
        return None

    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def map_directory(
    directory: str,
    save_json: bool = True,
    json_path: str = "tree.json",
):
    """Map a directory tree and collect stack detection details."""
    detector = StackDetector()
    directory = os.path.abspath(directory)
    ignore = load_ignore(directory)
    stats = {"files": 0, "folders": 0, "ignored": 0}

    def is_ignored(path: str):
        if ignore is None:
            return False

        relative_path = os.path.relpath(path, directory).replace(os.sep, "/")
        return ignore.match_file(relative_path)

    def build_tree(path: str):
        tree = {}

        try:
            items = sorted(os.listdir(path), key=lambda x: x.lower())
        except PermissionError:
            print(c(f" ! No permission: {path}", YELLOW))
            return tree

        for item in items:
            item_path = os.path.join(path, item)

            if is_ignored(item_path):
                stats["ignored"] += 1
                relative_path = os.path.relpath(item_path, directory)
                print(c(f"  > ignored  {relative_path}", GRAY))
                continue

            if os.path.isdir(item_path):
                stats["folders"] += 1
                stack = detector.detect(item, False)

                if stack:
                    detector.add_stack(stack, item_path)

                tree[item] = build_tree(item_path)
                continue

            stats["files"] += 1
            stack = detector.detect(item, True)

            if stack:
                detector.add_stack(stack, item_path)

            tree[item] = None

        return tree

    root_name = os.path.basename(directory)
    print(c(f"  {c('>', GREEN)} Analyzing {c(root_name, WHITE)}...", WHITE))

    tree = {root_name: build_tree(directory)}

    if save_json:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(tree, f, indent=4, ensure_ascii=False)

    return tree, detector.detected, stats


def show_tree(tree: dict):
    """Print the mapped project tree."""
    title("PROJECT TREE")

    def print_node(node: dict, prefix=""):
        items = list(node.items())

        for i, (name, content) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "

            if isinstance(content, dict):
                print(prefix + c(connector, CYAN) + c("/", BLUE) + c(name, WHITE))
                print_node(content, prefix + ("    " if is_last else "│   "))
                continue

            extension = Path(name).suffix
            icon = "" if extension else ":"
            color = WHITE if extension else GRAY
            print(prefix + c(connector, GRAY) + c(f"{icon} ", CYAN) + c(name, color))

    root, content = next(iter(tree.items()))
    print(c("> ", MAGENTA) + c(root, BOLD + WHITE))
    print_node(content)


def show_stacks(stacks: dict, stats: dict | None = None):
    """Print detected stacks and return their runtime list."""
    title("DETECTED STACKS")
    stack_list: list[str] = []

    if not stacks:
        print(c("  ! No stacks detected.", YELLOW))
        return stack_list

    total = len(stacks)
    plural = "s" if total != 1 else ""

    print(c(f"  {total} stack{plural} detected", GRAY))
    print()

    for index, (stack, paths) in enumerate(sorted(stacks.items())):
        is_last = index == len(stacks) - 1
        runtime = find_runtime(stack)

        if runtime and runtime not in stack_list:
            stack_list.append(runtime)

        print(
            c("└── " if is_last else "├── ", GRAY)
            + c("◆ ", GREEN)
            + c(stack, BOLD + WHITE)
        )

        if runtime:
            print(c("    ├── runtime: ", GRAY) + c(runtime, CYAN))

        for path_index, path in enumerate(paths):
            is_last_path = path_index == len(paths) - 1

            if is_last:
                prefix = "    └── " if is_last_path else "    ├── "
            else:
                prefix = "│   └── " if is_last_path else "│   ├── "

            print(c(prefix, GRAY) + c(os.path.normpath(path), DIM + WHITE))

        print(c("│", GRAY) if not is_last else "")

    return stack_list


def show_summary(stats: dict, stacks: dict, stack_list: list[str]):
    """Print scan totals."""
    title("SCAN SUMMARY")

    total_stacks = len(stacks)
    print(f"  {c('FILES', CYAN):<20}{stats['files']}")
    print(f"  {c('FOLDERS', CYAN):<20}{stats['folders']}")
    print(f"  {c('IGNORED', CYAN):<20}{stats['ignored']}")
    print(f"  {c('STACKS', CYAN):<20}{total_stacks}")
    print(f"  {c('RUNTIMES', CYAN):<20}{len(stack_list)}")
    print()


def main_dirtrain(directory: str):
    """Scan a project and return its tree plus detected runtimes."""
    title("HARBOR <SCAN>")

    print(c("  Target  ", GRAY) + c(os.path.abspath(directory), WHITE))
    print()

    tree, stacks, stats = map_directory(directory)
    show_tree(tree)
    stack_list = show_stacks(stacks, stats)
    show_summary(stats, stacks, stack_list)

    print(c("OK Scan concluded.", GREEN))
    print()

    return tree, stack_list
