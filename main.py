import argparse
from pathlib import Path

from ContainerStuff.access import restore_container
from ContainerStuff.compatibility import test_compatibility
from ContainerStuff.install import install_project
from ContainerStuff.runinstall import run_line
from ContainerStuff.wrapper import decompress_harb, main_wrapper
from ContainerStuff.WrapperStuff.hashflux import update_hash
from ContainerStuff.WrapperStuff.verifyflux import verify


def main():
    parser = argparse.ArgumentParser(description="Harbor commands")

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Sub-command to run",
    )

    # ========================================================
    # compatibility
    # ========================================================

    compatibility = subparsers.add_parser(
        "compatibility",
        help="Test compatibility of the project directory",
    )

    compatibility.add_argument(
        "path",
        type=Path,
        help="Path to the project directory.",
    )

    # ========================================================
    # verify
    # ========================================================

    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify the integrity of the project directory",
    )

    verify_parser.add_argument(
        "path",
        type=Path,
        help="Path to the project directory.",
    )

    # ========================================================
    # uphash
    # ========================================================

    hash_parser = subparsers.add_parser(
        "uphash",
        help="Update the hash of the project directory",
    )

    hash_parser.add_argument(
        "path",
        type=Path,
        help="Path to the project directory.",
    )

    # ========================================================
    # restore
    # ========================================================

    restore = subparsers.add_parser(
        "restore",
        help="Restore a container from a .harb file",
    )

    restore.add_argument(
        "file",
        type=Path,
        help="Path to the .harb file to restore.",
    )

    restore.add_argument(
        "--out",
        type=Path,
        default=Path("."),
        help="Output directory.",
    )

    restore.add_argument(
        "--password",
        required=True,
        help="Password for decrypting the container.",
    )

    # ========================================================
    # wrapper
    # ========================================================

    wrapper = subparsers.add_parser(
        "wrapper",
        help="Wrapper command for the project directory",
    )

    wrapper.add_argument(
        "path",
        type=Path,
        help="Path to the project directory.",
    )

    # ========================================================
    # inflate
    # ========================================================

    inflate = subparsers.add_parser(
        "inflate",
        help="Inflate a container from a .harb file",
    )

    inflate.add_argument(
        "file",
        type=Path,
        help="Path to the .harb file to inflate.",
    )

    inflate.add_argument(
        "--out",
        type=Path,
        default=Path("."),
        help="Output directory.",
    )

    # ========================================================
    # run
    # ========================================================

    run = subparsers.add_parser(
        "run",
        help="Run the .harbinstall script",
    )

    run.add_argument(
        "path",
        type=Path,
        help=("Path to the project directory, always from the root directory."),
    )

    # ========================================================
    # install
    # ========================================================

    install = subparsers.add_parser(
        "install",
        help="Install a project from GitHub",
    )

    install.add_argument(
        "target",
        help="Repository target in the form user/repo@version",
    )

    install.add_argument(
        "--os",
        dest="target_os",
        help="Target operating system. Defaults to the current OS.",
    )

    install.add_argument(
        "--arch",
        dest="target_architecture",
        help="Target architecture. Defaults to the current architecture.",
    )

    install.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Ignore compatibility scoring and use only command filters.",
    )

    install.add_argument(
        "-b",
        "--branch",
        dest="target_branch",
        help="Git branch to use when downloading HarborMap.yaml. Defaults to default.",
    )

    # ========================================================
    # PARSE
    # ========================================================

    args = parser.parse_args()

    # ========================================================
    # COMMANDS
    # ========================================================

    if args.command == "compatibility":
        test_compatibility(args.path)

    elif args.command == "verify":
        verify(args.path)

    elif args.command == "uphash":
        update_hash(args.path)

    elif args.command == "restore":
        restore_container(
            args.file,
            args.password,
            args.out,
        )

    elif args.command == "wrapper":
        main_wrapper(args.path)

    elif args.command == "inflate":
        decompress_harb(
            args.file,
            args.out,
        )

    elif args.command == "run":
        run_line(args.path)

    elif args.command == "install":
        return install_project(
            target=args.target,
            target_os=args.target_os,
            target_architecture=args.target_architecture,
            force=args.force,
            target_branch=args.target_branch,
        )


if __name__ == "__main__":
    main()
