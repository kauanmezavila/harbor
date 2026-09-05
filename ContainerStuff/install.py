import argparse
import os
import platform
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import yaml

from ContainerStuff.access import restore_container
from ContainerStuff.compatibility import normalize_arch, normalize_os, parse_version
from ContainerStuff.runinstall import run_line
from ContainerStuff.wrapper import decompress_harb
from ContainerStuff.WrapperStuff.verifyflux import verify

# ============================================================
# CONFIG
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"


# ============================================================
# MODELS
# ============================================================


@dataclass(frozen=True)
class RuntimeRequirement:
    language: str
    operator: str
    version: tuple[int, ...]


@dataclass
class Environment:
    target_os: str
    target_architecture: str
    runtimes: dict[str, str]


@dataclass
class Candidate:
    variant: dict[str, Any]
    version: tuple[int, ...]
    specificity: int


# ============================================================
# RUNTIME
# ============================================================

RUNTIME_ALIASES = {
    "python3": "python",
}

RUNTIME_COMMANDS = {
    "python": ("python", "python3"),
    "node": ("node",),
    "go": ("go",),
}


def normalize_runtime_name(name: Any) -> str | None:
    if name is None:
        return None

    normalized = str(name).strip().lower()

    if not normalized:
        return None

    return RUNTIME_ALIASES.get(
        normalized,
        normalized,
    )


def extract_version(text: str | None) -> str | None:
    if not text:
        return None

    match = re.search(
        r"(?<!\d)(\d+(?:\.\d+)+)(?!\d)",
        text,
    )

    if not match:
        return None

    version = match.group(1)

    if parse_version(version) is None:
        return None

    return version


def detect_runtime_version(
    runtime: str,
) -> str | None:

    runtime = normalize_runtime_name(runtime)  # type: ignore

    if runtime is None:
        return None

    commands = RUNTIME_COMMANDS.get(
        runtime,
        (runtime,),
    )

    for command in commands:
        if runtime == "go":
            attempts = [
                (command, "version"),
            ]
        else:
            attempts = [
                (command, "--version"),
                (command, "-v"),
            ]

        for args in attempts:
            try:
                result = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
            except (
                OSError,
                subprocess.SubprocessError,
            ):
                continue

            output = "\n".join(
                part
                for part in (
                    result.stdout,
                    result.stderr,
                )
                if part
            )

            version = extract_version(output)

            if version is not None:
                return version

    return None


def detect_runtimes(
    requirements: list[RuntimeRequirement],
) -> dict[str, str]:

    runtimes: dict[str, str] = {}

    languages = {requirement.language for requirement in requirements}

    for language in languages:
        version = detect_runtime_version(language)

        if version is not None:
            runtimes[language] = version

    return runtimes


# ============================================================
# VERSION / REQUIREMENT
# ============================================================

REQUIREMENT_PATTERN = re.compile(
    r"\s*([a-zA-Z0-9_-]+)\s*" r"(>=|<=|==|>|<)\s*" r"([0-9]+(?:\.[0-9]+)*)\s*"
)


def parse_requirement(
    value: Any,
) -> RuntimeRequirement | None:

    if not isinstance(value, str):
        return None

    match = REQUIREMENT_PATTERN.fullmatch(value)

    if not match:
        return None

    language = normalize_runtime_name(match.group(1))
    operator = match.group(2)
    version_text = match.group(3)

    if language is None:
        return None

    version = parse_version(version_text)

    if version is None:
        return None

    return RuntimeRequirement(
        language=language,
        operator=operator,
        version=tuple(version),
    )


def normalize_version(
    value: Any,
) -> tuple[int, ...] | None:

    if value is None:
        return None

    version = parse_version(str(value))

    if version is None:
        return None

    values = list(version)

    # 1.2 == 1.2.0
    while len(values) > 1 and values[-1] == 0:
        values.pop()

    return tuple(values)


def versions_equal(
    left: Any,
    right: Any,
) -> bool:

    left_version = normalize_version(left)
    right_version = normalize_version(right)

    if left_version is None or right_version is None:
        return str(left).strip() == str(right).strip()

    return left_version == right_version


def runtime_satisfies(
    requirement: RuntimeRequirement,
    installed_version: str,
) -> bool:

    installed = normalize_version(installed_version)

    if installed is None:
        return False

    required = requirement.version

    if requirement.operator == ">=":
        return installed >= required

    if requirement.operator == ">":
        return installed > required

    if requirement.operator == "==":
        return installed == required

    if requirement.operator == "<=":
        return installed <= required

    if requirement.operator == "<":
        return installed < required

    return False


# ============================================================
# YAML REQUIREMENTS
# ============================================================


def get_runtime_requirements(
    variants: list[Any],
) -> list[RuntimeRequirement]:

    requirements: list[RuntimeRequirement] = []
    languages: set[str] = set()

    for variant in variants:
        if not isinstance(variant, dict):
            continue

        requirement = parse_requirement(variant.get("runtime"))

        if requirement is None:
            continue

        if requirement.language in languages:
            continue

        languages.add(requirement.language)
        requirements.append(requirement)

    return requirements


# ============================================================
# ARCHITECTURE
# ============================================================


def parse_architectures(
    value: Any,
) -> list[str]:

    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        values = value
    elif isinstance(value, str):
        values = value.split(",")
    else:
        values = [value]

    result: list[str] = []

    for item in values:
        if item is None:
            continue

        normalized = normalize_arch(str(item).strip())

        if normalized and normalized not in result:
            result.append(normalized)

    return result


def architecture_matches(
    variant_architecture: Any,
    target_architecture: str,
) -> bool:

    architectures = parse_architectures(variant_architecture)

    if not architectures:
        return True

    if "any" in architectures:
        return True

    return target_architecture in architectures


# ============================================================
# COMPATIBILITY
# ============================================================


def os_matches(
    variant_os: Any,
    target_os: str,
) -> bool:

    if variant_os is None:
        return True

    variant_os = str(variant_os).strip()

    if not variant_os:
        return True

    normalized = normalize_os(variant_os)

    return normalized in {
        "any",
        target_os,
    }


def runtime_matches_variant(
    requirement_value: Any,
    runtimes: dict[str, str],
) -> bool:

    if requirement_value is None:
        return True

    if str(requirement_value).strip() == "":
        return True

    requirement = parse_requirement(requirement_value)

    if requirement is None:
        return False

    installed = runtimes.get(requirement.language)

    if installed is None:
        return False

    return runtime_satisfies(
        requirement,
        installed,
    )


def variant_matches(
    variant: dict[str, Any],
    environment: Environment,
) -> bool:

    if not os_matches(
        variant.get("os"),
        environment.target_os,
    ):
        return False

    if not architecture_matches(
        variant.get("architecture"),
        environment.target_architecture,
    ):
        return False

    return runtime_matches_variant(
        variant.get("runtime"),
        environment.runtimes,
    )


def forced_variant_matches(
    variant: dict[str, Any],
    target_os: str | None,
    target_architecture: str | None,
) -> bool:

    if target_os is not None:
        variant_os = variant.get("os")

        if variant_os is None or normalize_os(str(variant_os).strip()) != target_os:
            return False

    if target_architecture is not None:
        architectures = parse_architectures(variant.get("architecture"))

        if target_architecture not in architectures:
            return False

    return True


# ============================================================
# SPECIFICITY
# ============================================================


def specificity_score(
    variant: dict[str, Any],
) -> int:

    score = 0

    variant_os = variant.get("os")

    if (
        variant_os is not None
        and str(variant_os).strip()
        and normalize_os(str(variant_os).strip()) != "any"
    ):
        score += 1

    architectures = parse_architectures(variant.get("architecture"))

    if architectures and "any" not in architectures:
        score += 1

    runtime = variant.get("runtime")

    if runtime is not None and str(runtime).strip():
        score += 1

    return score


# ============================================================
# RESOLVER
# ============================================================


def resolve_variants(
    variants: list[Any],
    target_os: str | None = None,
    target_architecture: str | None = None,
    installed_runtimes: dict[str, str] | None = None,
    force: bool = False,
) -> dict[str, Any]:

    if not isinstance(variants, list):
        raise TypeError("'variants' must be a list")

    has_forced_target_os = target_os is not None
    has_forced_target_architecture = target_architecture is not None

    target_os = normalize_os(target_os or platform.system())

    target_architecture = normalize_arch(target_architecture or platform.machine())

    requirements = get_runtime_requirements(variants)

    if installed_runtimes is None:
        runtimes = detect_runtimes(requirements)
    else:
        runtimes = {}

        for language, version in installed_runtimes.items():
            normalized_language = normalize_runtime_name(language)

            if normalized_language is None:
                continue

            runtimes[normalized_language] = str(version)

    environment = Environment(
        target_os=(target_os if not force or has_forced_target_os else "any"),
        target_architecture=(
            target_architecture
            if not force or has_forced_target_architecture
            else "any"
        ),
        runtimes=runtimes,
    )

    candidates: list[Candidate] = []

    for variant in variants:
        if not isinstance(variant, dict):
            continue

        matches = (
            forced_variant_matches(
                variant,
                target_os if force and has_forced_target_os else None,
                (
                    target_architecture
                    if force and has_forced_target_architecture
                    else None
                ),
            )
            if force
            else variant_matches(
                variant,
                environment,
            )
        )

        if not matches:
            continue

        version = normalize_version(variant.get("version"))

        if version is None:
            continue

        candidates.append(
            Candidate(
                variant=variant,
                version=version,
                specificity=specificity_score(variant),
            )
        )

    # Priority:
    # 1. Newest compatible project version.
    # 2. Highest specificity for equal versions unless forced.
    candidates.sort(
        key=lambda candidate: (
            candidate.version,
            0 if force else candidate.specificity,
        ),
        reverse=True,
    )

    return {
        "selected": (candidates[0].variant if candidates else None),
        "candidates": candidates,
        "environment": environment,
        "requirements": requirements,
    }


# ============================================================
# GITHUB
# ============================================================


def download_harbor_map(
    user: str,
    repo: str,
    branch: str | None = None,
) -> dict[str, Any]:

    api_url = (
        f"https://api.github.com/repos/"
        f"{user}/{repo}/contents/"
        f"HarborSpecs/HarborMap.yaml"
    )

    if branch is not None:
        api_url += f"?ref={branch}"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "harbor-cli",
    }

    response = requests.get(
        api_url,
        timeout=20,
        headers=headers,
    )

    response.raise_for_status()

    data = response.json()

    download_url = data.get("download_url")

    if not download_url:
        raise RuntimeError("GitHub did not provide a download URL for HarborMap.yaml")

    file_response = requests.get(
        download_url,
        timeout=20,
        headers={
            "User-Agent": "harbor-cli",
        },
    )

    file_response.raise_for_status()

    try:
        content = yaml.safe_load(file_response.text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid HarborMap.yaml: {exc}") from exc

    if not isinstance(content, dict):
        raise TypeError("HarborMap.yaml must contain a YAML object")

    return content


def download_variant_harb(
    user: str,
    repo: str,
    variant_path: str,
    branch: str | None = None,
    output_dir: Path | None = None,
) -> Path:

    api_url = (
        f"https://api.github.com/repos/"
        f"{user}/{repo}/contents/HarborSpecs/"
        f"{variant_path}"
    )

    if branch is not None:
        api_url += f"?ref={branch}"

    response = requests.get(
        api_url,
        timeout=20,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "harbor-cli",
        },
    )
    response.raise_for_status()

    data = response.json()
    if not isinstance(data, dict):
        raise TypeError(
            f"GitHub did not return a valid metadata object for {variant_path}"
        )
    download_url = data.get("download_url")

    if not download_url:
        raise RuntimeError(f"GitHub did not provide a download URL for {variant_path}")

    file_response = requests.get(
        download_url,
        timeout=20,
        headers={
            "User-Agent": "harbor-cli",
        },
    )
    file_response.raise_for_status()

    output_dir = (
        Path(output_dir).expanduser().resolve()
        if output_dir is not None
        else Path.cwd()
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = Path(variant_path).name
    output_path = output_dir / filename
    output_path.write_bytes(file_response.content)

    return output_path


# ============================================================
# COMMAND PARSING
# ============================================================


def parse_install_command(
    command: str,
) -> tuple[str, str, str, str | None, str | None, bool, str | None]:

    args = shlex.split(command)

    if len(args) < 3 or args[0] != "harbor" or args[1] != "install":
        raise ValueError("Expected: harbor install user/repo@version")

    target: list[str] = []
    target_os: str | None = None
    target_arch: str | None = None
    target_branch: str | None = None
    force = False

    index = 2

    while index < len(args):
        arg = args[index]

        if arg in {"-f", "--force"}:
            force = True
            index += 1
            continue

        if arg == "--os":
            if index + 1 >= len(args):
                raise ValueError("--os requires a value")

            target_os = args[index + 1]
            index += 2
            continue

        if arg == "--arch":
            if index + 1 >= len(args):
                raise ValueError("--arch requires a value")

            target_arch = args[index + 1]
            index += 2
            continue

        if arg in {"-b", "--branch"}:
            if index + 1 >= len(args):
                raise ValueError("--branch requires a value")

            target_branch = args[index + 1]
            index += 2
            continue

        if arg.startswith("--"):
            raise ValueError(f"Unknown option: {arg}")

        target.append(arg)
        index += 1

    if len(target) != 1:
        raise ValueError("Expected one target: user/repo@version")

    owner, repo, version = parse_install_target(target[0])

    return (owner, repo, version, target_os, target_arch, force, target_branch)


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="harbor",
        description="Harbor package resolver",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    install_parser = subparsers.add_parser(
        "install",
        help="Resolve and install a project variant",
    )

    install_parser.add_argument(
        "target",
        nargs="+",
        metavar="TARGET",
        help=("Repository target. Example: user/repo@latest"),
    )

    install_parser.add_argument(
        "--os",
        dest="target_os",
        metavar="OS",
        help=("Target operating system. Defaults to the current OS."),
    )

    install_parser.add_argument(
        "--arch",
        dest="target_architecture",
        metavar="ARCH",
        help=("Target architecture. Defaults to the current architecture."),
    )

    install_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Ignore compatibility scoring and use only command filters.",
    )

    install_parser.add_argument(
        "-b",
        "--branch",
        dest="target_branch",
        metavar="BRANCH",
        help="Git branch to use when downloading HarborMap.yaml. Defaults to default.",
    )

    return parser


# ============================================================
# DISPLAY
# ============================================================


def print_resolution(
    result: dict[str, Any],
) -> tuple[str, dict[int, str] | None] | tuple[None, None]:

    environment: Environment = result["environment"]
    selected = result["selected"]
    candidates: list[Candidate] = result["candidates"]
    requirements: list[RuntimeRequirement] = result["requirements"]

    print()

    print(f"{BOLD}Target{RESET}")
    print(f"  OS:           {MAGENTA}{environment.target_os}{RESET}")
    print(f"  Architecture: {MAGENTA}{environment.target_architecture}{RESET}")

    print(f"\n{BOLD}Runtimes required by YAML{RESET}")

    if requirements:
        for requirement in requirements:
            version = environment.runtimes.get(requirement.language)

            if version is None:
                print(f"  {requirement.language}: {RED}not found{RESET}")
            else:
                print(f"  {requirement.language}: {MAGENTA}{version}{RESET}")
    else:
        print("  None")

    print(f"\n{BOLD}Selected{RESET}")

    if selected is None:
        print(f"  [{RED}NONE{RESET}] No compatible variant found.")
        return None, None

    print(f"  Path:    {YELLOW}{selected.get('path', 'unknown')}{RESET}")
    print(f"  Version: {YELLOW}{selected.get('version', 'unknown')}{RESET}")
    print(f"  OS:      {YELLOW}{selected.get('os', 'Any')}{RESET}")
    print(f"  Arch:    {YELLOW}{selected.get('architecture', 'Any')}{RESET}")
    print(f"  Runtime: {YELLOW}{selected.get('runtime', 'Any')}{RESET}")

    print(f"\n{BOLD}Candidates{RESET}")

    other_candidates: dict[int, str] | None = {}
    if candidates is not None:
        for index, candidate in enumerate(
            candidates,
            start=1,
        ):
            variant = candidate.variant

            print(
                f"  {index}. "
                f"{MAGENTA}"
                f"{variant.get('path', 'unknown')}"
                f"{RESET} "
                f"| version="
                f"{MAGENTA}"
                f"{variant.get('version', 'unknown')}"
                f"{RESET} "
                f"| specificity="
                f"{MAGENTA}"
                f"{candidate.specificity}"
                f"{RESET}"
            )
            other_candidates[index] = variant.get("path", "unknown")

        selected_path: str = selected.get("path", "unknown")

        return selected_path, other_candidates

    else:
        print("  None")
        return None, None


# ============================================================
# MAIN
# ============================================================


def parse_install_target(
    target: str,
) -> tuple[str, str, str]:

    if "@" not in target:
        raise ValueError(
            "Repository target must contain a version, for example: user/repo@latest"
        )

    repository, version = target.rsplit("@", 1)

    if "/" not in repository:
        raise ValueError("Repository must use the form user/repo@version")

    user, repo = repository.split("/", 1)

    user = user.strip()
    repo = repo.strip()
    version = version.strip()

    if not user or not repo:
        raise ValueError("Invalid GitHub repository")

    if not version:
        raise ValueError("Version cannot be empty")

    return user, repo, version


def install_project(
    target: str,
    target_os: str | None = None,
    target_architecture: str | None = None,
    force: bool = False,
    target_branch: str | None = None,
) -> int:

    try:
        # ----------------------------------------------------
        # Repository / version
        # ----------------------------------------------------

        user, repo, requested_version = parse_install_target(target)

        # ----------------------------------------------------
        # Target OS
        # ----------------------------------------------------

        normalized_os = None

        if target_os is not None:
            normalized_os = normalize_os(target_os)

            if not normalized_os:
                raise ValueError("--os cannot be empty")

        # ----------------------------------------------------
        # Target architecture
        # ----------------------------------------------------

        normalized_architecture = None

        if target_architecture is not None:
            normalized_architecture = normalize_arch(target_architecture)

            if not normalized_architecture:
                raise ValueError("--arch cannot be empty")

        # ----------------------------------------------------
        # Download HarborMap.yaml
        # ----------------------------------------------------

        data = download_harbor_map(user, repo, target_branch)

        project_name = data.get(
            "project",
            "Unknown",
        )

        description = data.get(
            "description",
            "Unknown",
        )

        variants = data.get("variants")

        if not isinstance(variants, list):
            raise TypeError("HarborMap.yaml does not contain a valid 'variants' list")

        # ----------------------------------------------------
        # Filter requested version
        # ----------------------------------------------------

        if requested_version != "latest":
            variants = [
                variant
                for variant in variants
                if (
                    isinstance(variant, dict)
                    and versions_equal(
                        variant.get("version"),
                        requested_version,
                    )
                )
            ]

            if not variants:
                raise ValueError(f"No variant found for version {requested_version}")

        # ----------------------------------------------------
        # Project information
        # ----------------------------------------------------

        print(f"{BOLD}{project_name}{RESET}, by {CYAN}{user}{RESET}")

        print(f"{DIM}{description}{RESET}")

        # ----------------------------------------------------
        # Resolve variant
        # ----------------------------------------------------

        result = resolve_variants(
            variants=variants,
            target_os=normalized_os,
            target_architecture=normalized_architecture,
            force=force,
        )

        # ----------------------------------------------------
        # Display resolution
        # ----------------------------------------------------

        print_resolution(result)

        # ----------------------------------------------------
        # No compatible variant
        # ----------------------------------------------------

        if result["selected"] is None:
            return 1

        # ----------------------------------------------------
        # Actual installation
        # ----------------------------------------------------

        print(
            "\n(0: the selected variant, or enter the index of another candidate to install)"
        )
        version_to_install = input(
            "Enter the version index to install (-1 to cancel): "
        ).strip()

        if version_to_install == "-1":
            print("Installation canceled.")
            return 0

        if not version_to_install.isdigit():
            print(
                f"[{RED}ERROR{RESET}] Invalid index: {version_to_install}",
                file=sys.stderr,
            )
            return 1

        index = int(version_to_install)
        candidate_list: list[Candidate] = result["candidates"]

        if index == 0:
            candidate = candidate_list[0]
        elif 1 <= index <= len(candidate_list):
            candidate = candidate_list[index - 1]
        else:
            print(
                f"[{RED}ERROR{RESET}] Invalid index: {index}",
                file=sys.stderr,
            )
            return 1

        downloaded_harb = download_variant_harb(
            user,
            repo,
            candidate.variant["path"],
            branch=target_branch,
        )

        print(f"[{GREEN} OK {RESET}] " f"Downloaded candidate: {downloaded_harb}")

        if downloaded_harb.suffix == ".harb":
            project_integrity = verify(downloaded_harb)

            if not project_integrity:
                print(f"{BOLD}[{RED}PANIC{WHITE}] HARB CONTAINER COMPROMISED!{RESET}")
                delete_ask = str(input("Delete container? [Y/n]: ")).strip().lower()

                if delete_ask == "n":
                    print(
                        f"[{GREEN} OK {RESET}] Caution, reviewing before download is HIGHLY recommended"
                    )
                else:
                    os.remove(downloaded_harb)
                    print(f"\n[{GREEN} OK {RESET}] Deleted.")
                    return 0

            inflate_ask = str(input("Want to inflate? [Y/n]: ")).strip().lower()

            if inflate_ask == "n":
                return 0

            else:
                container = decompress_harb(downloaded_harb)

                run_ask = (
                    str(input("Want to run .harbinstall? [Y/n]: ")).strip().lower()
                )

                if run_ask == "n":
                    return 0

                else:
                    run_line(container)

        if downloaded_harb.suffix == ".bcb":
            inflate_ask = str(input("Want to inflate? [Y/n]: ")).strip().lower()

            if inflate_ask == "n":
                return 0

            else:
                passwd = str(input("Type the password: "))
                container = restore_container(downloaded_harb, passwd)

                project_integrity = verify(container)

                if not project_integrity:
                    print(
                        f"{BOLD}[{RED}PANIC{WHITE}] HARB CONTAINER COMPROMISED!{RESET}"
                    )
                    delete_ask = str(input("Delete container? [Y/n]: ")).strip().lower()

                    if delete_ask == "n":
                        print(
                            f"[{GREEN} OK {RESET}] Caution, reviewing before download is HIGHLY recommended"
                        )
                    else:
                        os.remove(downloaded_harb)
                        os.remove(container)
                        print(f"\n[{GREEN} OK {RESET}] Deleted.")
                        return 0

                run_ask = (
                    str(input("Want to run .harbinstall? [Y/n]: ")).strip().lower()
                )

                if run_ask == "n":
                    return 0

                else:
                    run_line(container)

        return 0

    except requests.RequestException as exc:
        print(
            f"[{RED}ERROR{RESET}] GitHub request failed: {exc}",
            file=sys.stderr,
        )
        return 1

    except (
        ValueError,
        TypeError,
        RuntimeError,
    ) as exc:
        print(
            f"[{RED}ERROR{RESET}] {exc}",
            file=sys.stderr,
        )
        return 1
