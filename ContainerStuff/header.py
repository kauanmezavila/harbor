import json

from ContainerStuff.dirtrain import main_dirtrain


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

        default_project_name = list(tree.keys())[0]

        project_name = (
            input(
                f"Enter the project name "
                f"({default_project_name}): "
            ).strip()
            or default_project_name
        )

        project_version = (
            input(
                "Enter the project version (1.0.0): "
            ).strip()
            or "1.0.0"
        )

        # -------------------------------------------------
        # Architectures
        # -------------------------------------------------

        architecture_input = input(
            "Enter the project architectures "
            "(comma-separated, e.g. x86_64, arm64): "
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
            "Enter the supported operating systems "
            "(comma-separated, e.g. linux, windows): "
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
                "Enter the code owner/maintener name/alias: "
            ).strip()

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
            "Write a short description"
            "(press Enter to confirm): "
        )

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
            project_name + "-[HARBOR]",
        )

    header_data, project_name = build_header()

    with open(
        "header.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            header_data,
            f,
            indent=4,
            ensure_ascii=False,
        )

    print("[ OK ] Header created.")

    return project_name
