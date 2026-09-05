import argparse
import json
import platform
import re
import shutil
import subprocess
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


# ============================================================
# DIRECTORY
# ============================================================


def get_directory() -> Path:
    """Read and validate the project directory from CLI arguments."""

    parser = argparse.ArgumentParser(description="Analyse a project path.")

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


# ============================================================
# LANGUAGE / RUNTIME
# ============================================================


def extract_lang(cmd, version_args="--version"):
    """
    Try to find a program in the system and extract its version.

    Returns:
        str | None:
            Detected version or None if the program could not
            be found/executed.
    """

    if shutil.which(cmd) is None:
        return None

    try:
        result = subprocess.run(
            [cmd] + version_args.split(),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        output = (result.stdout or result.stderr).strip()

        if not output:
            return None

        match = re.search(
            r"\d+(?:\.\d+)+",
            output,
        )

        if match:
            return match.group(0)

        return output.splitlines()[0]

    except (
        subprocess.SubprocessError,
        OSError,
    ):
        return None


def parse_version(version):
    """
    Convert a version string into a tuple of integers.

    Examples:
        '3.13'   -> (3, 13)
        '3.13.5' -> (3, 13, 5)
        '22'     -> (22,)
    """

    try:
        return tuple(int(part) for part in version.split("."))

    except ValueError:
        return None


def compare_versions(installed, required):
    """
    Compare two version tuples.

    Missing components are treated as zero.
    """

    length = max(
        len(installed),
        len(required),
    )

    installed = installed + (0,) * (length - len(installed))

    required = required + (0,) * (length - len(required))

    return installed >= required


def check_langs(lang):
    """
    Check whether a required runtime is compatible
    with the version installed on the system.

    Expected format:

        python>=3.13
        node>=22
        go>=1.24
    """

    if ">=" not in lang:
        return {
            "status": "unsupported",
            "language": lang,
            "required": None,
            "installed": None,
        }

    command, required_version = lang.split(
        ">=",
        1,
    )

    command = command.strip()
    required_version = required_version.strip()

    if not command or not required_version:
        return {
            "status": "invalid",
            "language": command or lang,
            "required": required_version or None,
            "installed": None,
        }

    version_in_system = extract_lang(command)

    if version_in_system is None:
        return {
            "status": "not_found",
            "language": command,
            "required": required_version,
            "installed": None,
        }

    required = parse_version(required_version)

    installed = parse_version(version_in_system)

    if required is None or installed is None:
        return {
            "status": "invalid_version",
            "language": command,
            "required": required_version,
            "installed": version_in_system,
        }

    compatible = compare_versions(
        installed,
        required,
    )

    return {
        "status": ("compatible" if compatible else "wrong_version"),
        "language": command,
        "required": required_version,
        "installed": version_in_system,
    }


# ============================================================
# OS / ARCHITECTURE
# ============================================================


def normalize_os(value):
    """
    Normalize operating system names.

    Internal Harbor values:
        linux
        windows
        macos
        freebsd
    """

    aliases = {
        "linux": "linux",
        "gnu/linux": "linux",
        "windows": "windows",
        "win": "windows",
        "win32": "windows",
        "win64": "windows",
        "darwin": "macos",
        "mac": "macos",
        "macos": "macos",
        "osx": "macos",
        "freebsd": "freebsd",
    }

    value = str(value).strip().lower()

    return aliases.get(
        value,
        value,
    )


def normalize_arch(value):
    """
    Normalize architecture names.

    Internal Harbor values:
        x86_64
        arm64
        x86
        arm
    """

    aliases = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "x64": "x86_64",
        "x86-64": "x86_64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "x86": "x86",
        "i386": "x86",
        "i686": "x86",
        "arm": "arm",
        "arm32": "arm",
    }

    value = str(value).strip().lower()

    return aliases.get(
        value,
        value,
    )


def normalize_list(value, normalizer):
    """
    Normalize a compatibility value into a list.

    Accepts:
        ["linux", "windows"]
        "linux"
        None
    """

    if value is None:
        return []

    if isinstance(value, str):
        value = [value]

    if not isinstance(value, list):
        return []

    result = []

    for item in value:
        item = normalizer(item)

        if item and item not in result:
            result.append(item)

    return result


def check_os_and_arch(
    supported_os,
    supported_architectures,
):
    """
    Check whether the current system matches the
    operating systems and architectures supported
    by the Harbor project.

    Returns a structured result.
    """

    actual_os_raw = platform.system()
    actual_arch_raw = platform.machine()

    actual_os = normalize_os(actual_os_raw)

    actual_arch = normalize_arch(actual_arch_raw)

    supported_os = normalize_list(
        supported_os,
        normalize_os,
    )

    supported_architectures = normalize_list(
        supported_architectures,
        normalize_arch,
    )

    # --------------------------------------------------------
    # Empty compatibility fields
    # --------------------------------------------------------

    # If no OS is specified, we treat it as
    # "no OS restriction".
    os_compatible = not supported_os or actual_os in supported_os

    # Same idea for architecture.
    arch_compatible = (
        not supported_architectures or actual_arch in supported_architectures
    )

    compatible = os_compatible and arch_compatible

    return {
        "compatible": compatible,
        "os": {
            "actual": actual_os,
            "actual_raw": actual_os_raw,
            "supported": supported_os,
            "compatible": os_compatible,
        },
        "architecture": {
            "actual": actual_arch,
            "actual_raw": actual_arch_raw,
            "supported": supported_architectures,
            "compatible": arch_compatible,
        },
    }


# ============================================================
# COMPATIBILITY
# ============================================================


def test_compatibility(path=None):
    """
    Test whether the current system is compatible
    with the Harbor container/project.
    """

    directory = path if path else get_directory()

    directory = Path(directory).expanduser().resolve()

    if not directory.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERROR{RESET}] Project directory not found: {directory}"
        )

    if not directory.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERROR{RESET}] Project path is not a directory: {directory}"
        )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    info_path = directory / "Info" / "header.json"

    if not info_path.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERROR{RESET}] header.json not found: {info_path}"
        )

    if not info_path.is_file():
        raise FileNotFoundError(
            f"\n[{RED}ERROR{RESET}] Invalid header.json: {info_path}"
        )

    try:
        with open(
            info_path,
            "r",
            encoding="utf-8",
        ) as f:
            header_data = json.load(f)

    except json.JSONDecodeError as error:
        raise ValueError(f"\n[{RED}ERROR{RESET}] Invalid JSON in header.json: {error}")

    # --------------------------------------------------------
    # Project metadata
    # --------------------------------------------------------

    project_name = header_data.get(
        "PROJECT NAME",
        "Unknown",
    )

    project_version = header_data.get(
        "PROJECT VERSION",
        "Unknown",
    )

    compatibility = header_data.get(
        "COMPATIBILITY",
        {},
    )

    if not isinstance(
        compatibility,
        dict,
    ):
        compatibility = {}

    supported_architectures = compatibility.get(
        "ARCHITECTURES",
        [],
    )

    supported_os = compatibility.get(
        "OS",
        [],
    )

    stacks = header_data.get(
        "PROJECT STACKS",
        [],
    )

    if not isinstance(stacks, list):
        stacks = []

    # --------------------------------------------------------
    # Compatibility information
    # --------------------------------------------------------

    os_arch_result = check_os_and_arch(
        supported_os,
        supported_architectures,
    )

    actual_os = os_arch_result["os"]["actual"]

    actual_arch = os_arch_result["architecture"]["actual"]

    os_compatible = os_arch_result["os"]["compatible"]

    arch_compatible = os_arch_result["architecture"]["compatible"]

    # --------------------------------------------------------
    # Display header
    # --------------------------------------------------------

    print()

    print(f"{BOLD}{CYAN}========================================{RESET}")

    print(f"{BOLD}        HARBOR COMPATIBILITY{RESET}")

    print(f"{BOLD}{CYAN}========================================{RESET}")

    print()

    print(f"Project name:           {YELLOW}{project_name}{RESET}")

    print(f"Project version:        {YELLOW}{project_version}{RESET}")

    print()

    # --------------------------------------------------------
    # OS
    # --------------------------------------------------------

    supported_os_display = (
        ", ".join(os_arch_result["os"]["supported"])
        if os_arch_result["os"]["supported"]
        else "Any"
    )

    print(
        f"Operating system:       {YELLOW}{actual_os}{RESET} ({supported_os_display})"
    )

    if os_compatible:
        print(f"       {GREEN}OK{RESET} Operating system is supported.")
    else:
        print(f"       {RED}NO{RESET} Operating system is not supported.")

    # --------------------------------------------------------
    # Architecture
    # --------------------------------------------------------

    supported_arch_display = (
        ", ".join(os_arch_result["architecture"]["supported"])
        if os_arch_result["architecture"]["supported"]
        else "Any"
    )

    print()

    print(
        f"Architecture:           "
        f"{YELLOW}{actual_arch}{RESET} "
        f"({supported_arch_display})"
    )

    if arch_compatible:
        print(f"       {GREEN}OK{RESET} Architecture is supported.")
    else:
        print(f"       {RED}NO{RESET} Architecture is not supported.")

    # --------------------------------------------------------
    # Stacks
    # --------------------------------------------------------

    print()

    print(f"{BOLD}Stacks:{RESET}")

    if not stacks:
        print(f"       {YELLOW}- No stacks specified{RESET}")

    results = []

    for stack in stacks:
        result = check_langs(stack)

        results.append(result)

        language = result["language"]
        required = result["required"]
        installed = result["installed"]
        status = result["status"]

        if status == "compatible":
            print(
                f"       {GREEN}OK{RESET} "
                f"{language} >= {required} "
                f"(installed: {installed})"
            )

        elif status == "wrong_version":
            print(
                f"       {RED}NO{RESET} "
                f"{language} >= {required} "
                f"(installed: {installed})"
            )

        elif status == "not_found":
            print(
                f"       {RED}NO{RESET} {language} >= {required} (not found/installed)"
            )

        elif status == "unsupported":
            print(f"       {YELLOW}??{RESET} {stack} (unsupported requirement)")

        elif status == "invalid":
            print(f"       {RED}NO{RESET} {stack} (invalid requirement)")

        elif status == "invalid_version":
            print(
                f"       {RED}NO{RESET} "
                f"{language} >= {required} "
                f"(could not parse version: "
                f"{installed})"
            )

    # --------------------------------------------------------
    # Runtime compatibility
    # --------------------------------------------------------

    stacks_compatible = all(result["status"] == "compatible" for result in results)

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    compatible = os_compatible and arch_compatible and stacks_compatible

    print()

    print(f"{BOLD}{CYAN}========================================{RESET}")

    if compatible:
        print(f"{BOLD}{GREEN}       ENVIRONMENT COMPATIBLE{RESET}")

        print(f"{GREEN}  The project can run on this system.{RESET}")

    else:
        print(f"{BOLD}{RED}     ENVIRONMENT NOT COMPATIBLE{RESET}")

        if not os_compatible:
            print(f"     {RED}NO{RESET} Operating system mismatch.")

        if not arch_compatible:
            print(f"     {RED}NO{RESET} Architecture mismatch.")

        if not stacks_compatible:
            print(f"     {RED}NO{RESET} Runtime stack mismatch.")

    print(f"{BOLD}{CYAN}========================================{RESET}")

    print()

    return {
        "compatible": compatible,
        "project_name": project_name,
        "project_version": project_version,
        "os": os_arch_result["os"],
        "architecture": os_arch_result["architecture"],
        "stacks": results,
    }


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    test_compatibility()
