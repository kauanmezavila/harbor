import argparse
from pathlib import Path

from ContainerStuff.access import restore_container
from ContainerStuff.compatibility import test_compatibility
from ContainerStuff.WrapperStuff.hashflux import update_hash
from ContainerStuff.WrapperStuff.verifyflux import verify
from ContainerStuff.wrapper import main_wrapper, decompress_harb
from ContainerStuff.runinstall import run_line


def main():
    parser = argparse.ArgumentParser(description="Harbor commands")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-command to run")

    compatibility = subparsers.add_parser("compatibility", help="Test compatibility of the project directory")
    compatibility.add_argument("path", type=Path, help="Path to the project directory (default: current directory).")


    verify_parser = subparsers.add_parser("verify", help="Verify the integrity of the project directory")
    verify_parser.add_argument("path", type=Path, help="Path to the project directory (default: current directory).")


    hash_parser = subparsers.add_parser("uphash", help="Update the hash of the project directory")
    hash_parser.add_argument("path", type=Path, help="Path to the project directory (default: current directory).")


    restore = subparsers.add_parser("restore", help="Restore a container from a .harb file")
    restore.add_argument("file", type=Path, help="Path to the .harb file to restore.")
    restore.add_argument("--out", type=Path, default=Path("."), help="Output directory for the restored container (default: current directory).")
    restore.add_argument("--password", required=True, help="Password for decrypting the container.")


    wrapper = subparsers.add_parser("wrapper", help="Wrapper command for the project directory")
    wrapper.add_argument("path", type=Path, default=Path("."), help="Path to the project directory (default: current directory).")

    inflate = subparsers.add_parser("inflate", help="Inflate a container from a .harb file")
    inflate.add_argument("file", type=Path, help="Path to the .harb file to inflate.")
    inflate.add_argument("--out", type=Path, default=Path("."), help="Output directory for the inflated container (default: current directory).")

    install = subparsers.add_parser("install", help="Run the .harbinstall script in the project directory")
    install.add_argument("path", type=Path, default=Path("."), help="Path to the project directory, ALWAYS BY THE ROOT DIR (default: current directory).")

    args = parser.parse_args()

    if args.command == "compatibility":
        test_compatibility(args.path)

    elif args.command == "verify":
        verify(args.path)

    elif args.command == "uphash":
        update_hash(args.path)

    elif args.command == "restore":
        restore_container(args.file, args.password, args.out)

    elif args.command == "wrapper":
        main_wrapper(args.path)

    elif args.command == "inflate":
        decompress_harb(args.file, args.out)

    elif args.command == "install":
        run_line()

if __name__ == "__main__":
    main()