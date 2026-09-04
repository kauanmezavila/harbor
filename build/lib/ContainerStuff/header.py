import json

from ContainerStuff.dirtrain import main_dirtrain

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

def normalize_list(value):
    """
    Convert comma-separated input into a normalized list.

    Examples:
        "linux, windows" -> ["linux", "windows"]
        "x86_64, arm64"  -> ["x86_64", "arm64"]
    """

    if not value:
        return None

    values = [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]

    return values or None


def normalize_architecture(architecture):
    """
    Normalize architecture names to Harbor's standard names.
    """

    aliases = {
        "x64": "x86_64",
        "amd64": "x86_64",
        "x86-64": "x86_64",
        "x86_64": "x86_64",

        "aarch64": "arm64",
        "arm64": "arm64",

        "x86": "x86",
        "i386": "x86",
        "i686": "x86",

        "arm": "arm",
        "arm32": "arm",
    }

    architecture = architecture.strip().lower()

    return aliases.get(
        architecture,
        architecture,
    )


def normalize_os(system):
    """
    Normalize operating system names to Harbor's standard names.
    """

    aliases = {
        "linux": "linux",
        "gnu/linux": "linux",

        "windows": "windows",
        "win": "windows",
        "win32": "windows",
        "win64": "windows",

        "mac": "macos",
        "macos": "macos",
        "osx": "macos",

        "freebsd": "freebsd",
    }

    system = system.strip().lower()

    return aliases.get(
        system,
        system,
    )


def header(path):
    """Build the metadata header for a Harbor container."""

    def build_header():
        tree, stack_list = main_dirtrain(path)

        if not tree:
            raise ValueError(
                "Could not determine the project tree."
            )

        default_project_name = next(iter(tree))

        project_name = (
            input(
                f"Enter the {MAGENTA}project name{RESET} "
                f"({default_project_name}): "
            ).strip()
            or default_project_name
        )

        project_version = (
            input(
                f"Enter the {MAGENTA}project version{RESET} (1.0.0): "
            ).strip()
            or "1.0.0"
        )

        # -------------------------------------------------
        # Architectures
        # -------------------------------------------------

        architecture_input = input(
            f"Enter the {MAGENTA}project architectures{RESET} "
            "(comma-separated, e.g. x86_64, arm64. None = Any): "
        ).strip()

        architectures = normalize_list(
            architecture_input
        )

        if architectures:
            architectures = [
                normalize_architecture(
                    architecture
                )
                for architecture in architectures
            ]

            # Remove duplicates while preserving order.
            architectures = list(
                dict.fromkeys(architectures)
            )

        # -------------------------------------------------
        # Operating systems
        # -------------------------------------------------

        os_input = input(
            f"Enter the supported {MAGENTA}operating systems{RESET} "
            f"(comma-separated, e.g. linux, windows. None = Any): "
        ).strip()

        operating_systems = normalize_list(
            os_input
        )

        if operating_systems:
            operating_systems = [
                normalize_os(
                    system
                )
                for system in operating_systems
            ]

            # Remove duplicates while preserving order.
            operating_systems = list(
                dict.fromkeys(operating_systems)
            )

        # -------------------------------------------------
        # Owners name
        # -------------------------------------------------

        while True:
            owner_name = input(
                f"Enter the {MAGENTA}code owner/maintener name/alias{RESET}: "
            ).strip() or "Unknown"

            confirmation = input(
                f"'{owner_name}' is right?"
                " [y/n]: "
            ).strip().lower()

            if confirmation == "y":
                break

        # -------------------------------------------------
        # Short description
        # -------------------------------------------------

        short_description = input(
            f"Write a {MAGENTA}short description{RESET} "
            "(press Enter to confirm): "
        ).strip()

        # -------------------------------------------------
        # Final header
        # -------------------------------------------------

        final_header = {
            "PROJECT NAME": project_name,
            "PROJECT DESCRIPTION": short_description,
            "PROJECT VERSION": project_version,
            "PROJECT OWNER": owner_name,

            "COMPATIBILITY": {
                "ARCHITECTURES": architectures,
                "OS": operating_systems,
            },

            "PROJECT STACKS": stack_list,
            "PROJECT TREE": tree,
        }

        return (
            final_header,
            project_name
            + "-"
            + "-".join(
                architecture
                for architecture in (architectures or ["Any"])
                if architecture is not None
            )
            + "-"
            + "-".join(
                system
                for system in (operating_systems or ["Any"])
                if system is not None
            )
            + "-[HARBOR]",
        )

    header_data, project_name = build_header()

    header_file = path / "header.json"

    with open(
        header_file,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            header_data,
            f,
            indent=4,
            ensure_ascii=False,
        )

    print("\n[ OK ] Header created.")

    return project_name
