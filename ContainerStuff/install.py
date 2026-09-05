import os
import re
import shlex
import platform

import requests
import yaml

from compatibility import (
    normalize_arch,
    normalize_os,
    extract_lang,
    parse_version,
)

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

MAGENTA = "\033[95m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"


DEFAULT_USER = "kauanmezavila"
DEFAULT_REPO = "harbor"


# ============================================================
# VARIANT RESOLVER / RANKING ENGINE
# ============================================================

def parse_architectures(value):
    """
    Convert an architecture field into a normalized list.

    Supported:
        "x86_64"
        "x86_64, arm64"
        ["x86_64", "arm64"]
        "Any"
    """
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        values = value
    elif isinstance(value, str):
        values = value.split(",")
    else:
        values = [value]

    result = []

    for item in values:
        if item is None:
            continue

        item = str(item).strip()

        if not item:
            continue

        normalized = normalize_arch(item)

        if normalized not in result:
            result.append(normalized)

    return result


def parse_requirement(requirement):
    """
    Parse runtime requirements.

    Examples:
        python>=3.12
        python>=3.13
        node>=22
        go==1.24

    Returns:
        {
            "language": "python",
            "operator": ">=",
            "version": (3, 12)
        }

    Returns None for an invalid requirement.
    """
    if not isinstance(requirement, str):
        return None

    match = re.match(
        r"^\s*([a-zA-Z0-9_-]+)\s*"
        r"(>=|<=|==|>|<)\s*"
        r"([0-9]+(?:\.[0-9]+)*)\s*$",
        requirement,
    )

    if not match:
        return None

    language = match.group(1).lower()
    operator = match.group(2)
    version = parse_version(match.group(3))

    if version is None:
        return None

    return {
        "language": language,
        "operator": operator,
        "version": version,
    }


def runtime_matches(requirement, installed_version):
    """Check whether an installed runtime satisfies a requirement."""
    parsed = parse_requirement(requirement)

    if parsed is None:
        return False

    installed = parse_version(str(installed_version))

    if installed is None:
        return False

    required = parsed["version"]
    operator = parsed["operator"]

    if operator == ">=":
        return installed >= required

    if operator == ">":
        return installed > required

    if operator == "==":
        return installed == required

    if operator == "<=":
        return installed <= required

    if operator == "<":
        return installed < required

    return False


def get_runtime_versions():
    """
    Detect runtimes installed on the current system.

    Returns a dictionary such as:
        {
            "python": "3.13.5",
            "python3": "3.13.5",
            "node": "22.1.0",
            "go": "1.24.0"
        }
    """
    runtimes = {}

    for command in ("python", "python3", "node", "go"):
        try:
            version = extract_lang(command)
        except Exception:
            version = None

        if version:
            runtimes[command] = str(version)

    # Prefer one canonical Python entry when possible.
    if "python" not in runtimes and "python3" in runtimes:
        runtimes["python"] = runtimes["python3"]

    return runtimes


def score_os(variant_os, actual_os):
    """
    Return:
        (compatible, score, reason)

    Specific OS gets more priority than Any.
    """
    if variant_os is None or str(variant_os).strip() == "":
        return True, 10, "OS not specified"

    normalized = normalize_os(str(variant_os).strip())
    actual = normalize_os(str(actual_os).strip())

    if normalized == "any":
        return True, 10, "OS: Any"

    if normalized == actual:
        return True, 50, "Exact OS"

    return False, 0, "Incompatible OS"


def score_architecture(variant_architecture, actual_architecture):
    """
    Return:
        (compatible, score, reason)

    Supports multiple architectures:
        "x86_64, arm64"
        ["x86_64", "arm64"]
    """
    architectures = parse_architectures(variant_architecture)
    actual = normalize_arch(str(actual_architecture).strip())

    if not architectures:
        return True, 10, "Architecture not specified"

    if "any" in architectures:
        return True, 10, "Architecture: Any"

    if actual in architectures:
        if len(architectures) == 1:
            return True, 50, "Exact architecture"

        return True, 40, "Compatible architecture"

    return False, 0, "Incompatible architecture"


def score_runtime(requirement, installed_runtimes):
    """
    Return:
        (compatible, score, reason)
    """
    if requirement is None or str(requirement).strip() == "":
        return True, 10, "Runtime not specified"

    requirement = str(requirement).strip()
    parsed = parse_requirement(requirement)

    if parsed is None:
        return False, 0, f"Invalid runtime requirement: {requirement}"

    language = parsed["language"]

    installed = installed_runtimes.get(language)

    # Python fallback.
    if installed is None and language == "python":
        installed = installed_runtimes.get("python3")

    if installed is None:
        return False, 0, f"{language} not found"

    if not runtime_matches(requirement, installed):
        return (
            False,
            0,
            f"{language} {installed} does not satisfy {requirement}",
        )

    return (
        True,
        30,
        f"{language} {installed} satisfies {requirement}",
    )


def version_score(version):
    """
    Convert a project version into a sortable integer.

    Examples:
        1.2.0 > 1.1.0 > 1.0.0
    """
    parsed = parse_version(str(version))

    if parsed is None:
        return 0

    parts = list(parsed) + [0, 0, 0]

    major = parts[0]
    minor = parts[1]
    patch = parts[2]

    return (
        major * 1_000_000
        + minor * 1_000
        + patch
    )


def rank_variant(
    variant,
    actual_os,
    actual_architecture,
    installed_runtimes,
):
    """
    Classify one variant.

    The engine first checks compatibility. Only compatible
    variants receive a useful ranking score.
    """
    if not isinstance(variant, dict):
        return {
            "compatible": False,
            "score": 0,
            "version_score": 0,
            "variant": variant,
            "reasons": ["Invalid variant"],
        }

    reasons = []
    score = 0

    variant_os = variant.get("os", "Any")
    variant_arch = variant.get("architecture", "Any")
    runtime = variant.get("runtime")

    # --------------------------------------------------------
    # OS
    # --------------------------------------------------------

    os_ok, os_score, os_reason = score_os(
        variant_os,
        actual_os,
    )

    if not os_ok:
        return {
            "compatible": False,
            "score": 0,
            "version_score": 0,
            "variant": variant,
            "reasons": [os_reason],
        }

    score += os_score
    reasons.append(os_reason)

    # --------------------------------------------------------
    # Architecture
    # --------------------------------------------------------

    arch_ok, arch_score, arch_reason = score_architecture(
        variant_arch,
        actual_architecture,
    )

    if not arch_ok:
        return {
            "compatible": False,
            "score": 0,
            "version_score": 0,
            "variant": variant,
            "reasons": [arch_reason],
        }

    score += arch_score
    reasons.append(arch_reason)

    # --------------------------------------------------------
    # Runtime
    # --------------------------------------------------------

    runtime_ok, runtime_score_value, runtime_reason = score_runtime(
        runtime,
        installed_runtimes,
    )

    if not runtime_ok:
        return {
            "compatible": False,
            "score": 0,
            "version_score": 0,
            "variant": variant,
            "reasons": [runtime_reason],
        }

    score += runtime_score_value
    reasons.append(runtime_reason)

    # --------------------------------------------------------
    # Specificity
    # --------------------------------------------------------

    normalized_os = normalize_os(str(variant_os).strip())
    architectures = parse_architectures(variant_arch)

    # OS-specific variants beat Any.
    if normalized_os != "any":
        score += 20

    # Architecture-specific variants beat Any.
    if architectures and "any" not in architectures:
        score += 20

    # --------------------------------------------------------
    # Version
    # --------------------------------------------------------

    project_version = variant.get("version", "0.0.0")
    parsed_project_version = parse_version(str(project_version))
    variant_version_score = version_score(project_version)

    return {
        "compatible": True,
        "score": score,
        "version_score": variant_version_score,
        "version": (
            str(project_version)
            if parsed_project_version is not None
            else "0.0.0"
        ),
        "variant": variant,
        "reasons": reasons,
    }


def resolve_variants(
    variants,
    actual_os=None,
    actual_architecture=None,
    installed_runtimes=None,
):
    """
    Main variant resolution engine.

    Returns:

        {
            "selected": <best variant result or None>,
            "candidates": [<compatible variants>],
            "environment": {
                "os": "...",
                "architecture": "...",
                "runtimes": {...}
            }
        }
    """
    if not isinstance(variants, list):
        raise TypeError("'variants' must be a list")

    if actual_os is None:
        actual_os = normalize_os(platform.system())
    else:
        actual_os = normalize_os(str(actual_os))

    if actual_architecture is None:
        actual_architecture = normalize_arch(platform.machine())
    else:
        actual_architecture = normalize_arch(str(actual_architecture))

    if installed_runtimes is None:
        installed_runtimes = get_runtime_versions()

    ranked = []

    for variant in variants:
        result = rank_variant(
            variant=variant,
            actual_os=actual_os,
            actual_architecture=actual_architecture,
            installed_runtimes=installed_runtimes,
        )

        if result["compatible"]:
            ranked.append(result)

    # --------------------------------------------------------
    # Ranking
    #
    # First: compatibility/specificity score
    # Second: project version
    # --------------------------------------------------------

    ranked.sort(
        key=lambda result: (
            result["score"],
            result.get("version_score", 0),
        ),
        reverse=True,
    )

    return {
        "selected": ranked[0] if ranked else None,
        "candidates": ranked,
        "environment": {
            "os": actual_os,
            "architecture": actual_architecture,
            "runtimes": installed_runtimes,
        },
    }


# ============================================================
# GITHUB / HARBOR MAP
# ============================================================

def download_harb(user, repo):
    """
    Download HarborSpecs/HarborMap.yaml from GitHub.
    """
    api_url = (
        f"https://api.github.com/repos/"
        f"{user}/{repo}/contents/HarborSpecs/HarborMap.yaml"
    )

    response = requests.get(
        api_url,
        timeout=20,
        headers={
            "Accept": "application/vnd.github+json",
        },
    )
    response.raise_for_status()

    data = response.json()

    download_url = data.get("download_url")

    if not download_url:
        raise RuntimeError(
            "GitHub did not provide a download URL for HarborMap.yaml"
        )

    downloaded_file = requests.get(
        download_url,
        timeout=20,
    )
    downloaded_file.raise_for_status()

    cache_file = "HarborMap-Cache.yaml"

    try:
        with open(cache_file, "wb") as file:
            file.write(downloaded_file.content)

        with open(cache_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    finally:
        if os.path.exists(cache_file):
            os.remove(cache_file)


def resolve_install_cmd(command):
    """
    Parse:
        harbor install user/repo@version

    Also accepts:
        harbor install user repo@version
    """
    cmd = shlex.split(command)

    if len(cmd) < 3:
        raise ValueError(
            "Invalid install command. "
            "Expected: harbor install user/repo@version"
        )

    target = cmd[-1]

    if "@" not in target:
        raise ValueError(
            "Repository target must contain a version, "
            "for example: user/repo@latest"
        )

    repo_part, version = target.rsplit("@", 1)

    if "/" in repo_part:
        owner, repo = repo_part.split("/", 1)
    else:
        if len(cmd) < 4:
            raise ValueError(
                "Expected: harbor install user repo@version"
            )

        owner = cmd[2]
        repo = repo_part

    if not owner or not repo:
        raise ValueError("Invalid GitHub repository")

    return owner, repo, version


# ============================================================
# DISPLAY
# ============================================================

def print_resolution(result):
    """Pretty-print the resolver result."""
    environment = result["environment"]
    selected = result["selected"]
    candidates = result["candidates"]

    print()
    print(f"{BOLD}Environment{RESET}")
    print(f"  OS:           {environment['os']}")
    print(f"  Architecture: {environment['architecture']}")

    print(f"\n{BOLD}Runtimes{RESET}")

    if environment["runtimes"]:
        for name, version in environment["runtimes"].items():
            print(f"  {name}: {version}")
    else:
        print("  None detected")

    print(f"\n{BOLD}Selected{RESET}")

    if selected is None:
        print(f"  [{RED}NONE{RESET}] No compatible variant found.")
        return

    variant = selected["variant"]

    print(f"  Path:    {variant.get('path', 'unknown')}")
    print(f"  Version: {variant.get('version', 'unknown')}")
    print(f"  OS:      {variant.get('os', 'Any')}")
    print(f"  Arch:    {variant.get('architecture', 'Any')}")
    print(f"  Runtime: {variant.get('runtime', 'Any')}")
    print(f"  Score:   {selected['score']}")

    print(f"\n{BOLD}Candidates{RESET}")

    for index, candidate in enumerate(candidates, start=1):
        variant = candidate["variant"]

        print(
            f"  {index}. "
            f"{variant.get('path', 'unknown')} "
            f"| version={variant.get('version', 'unknown')} "
            f"| score={candidate['score']}"
        )

        for reason in candidate["reasons"]:
            print(f"     - {reason}")


# ============================================================
# MAIN
# ============================================================

def main():
    install_command = (
        "harbor install "
        f"{DEFAULT_USER}/{DEFAULT_REPO}@latest"
    )

    try:
        user, repo, requested_version = resolve_install_cmd(
            install_command
        )

        data = download_harb(user, repo)

        if not isinstance(data, dict):
            raise ValueError("HarborMap.yaml must contain a YAML object")

        project_name = data.get("project") or "Unknown"
        description = data.get("description") or "Unknown"
        variants = data.get("variants")

        if not isinstance(variants, list):
            raise ValueError(
                "HarborMap.yaml does not contain a valid 'variants' list"
            )

        print(f"{BOLD}{project_name}{RESET}")
        print(f"{DIM}{description}{RESET}")

        if requested_version != "latest":
            variants = [
                variant
                for variant in variants
                if str(variant.get("version")) == requested_version
            ]

        result = resolve_variants(variants)

        print_resolution(result)

    except requests.RequestException as e:
        print(
            f"[{RED}ERROR{RESET}] "
            f"GitHub request failed: {e}"
        )
    except Exception as e:
        print(
            f"[{RED}ERROR{RESET}] "
            f"{e}"
        )


if __name__ == "__main__":
    main()