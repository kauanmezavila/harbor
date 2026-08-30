<p align="center">
  <img src="imgs/Harbor.png" alt="Harbor logo" width="180">
</p>

<h1 align="center">Harbor</h1>

<p align="center">
  A lightweight open-source project container CLI for packaging, metadata, compatibility checks, integrity hashes, and encrypted exports.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-111111?style=for-the-badge">
  <img alt="Status" src="https://img.shields.io/badge/Status-v1.0.0-9b59b6?style=for-the-badge">
</p>

---

## What is Harbor?

Harbor is a terminal suite that wraps a project into a portable container-like folder.

It scans the project tree, detects known stacks, writes metadata, copies code into a clean `Code/` area, stores root information in `Info/`, creates recursive SHA-256 integrity hashes, and can export an encrypted `.bcb` archive.

It is not Docker. It is closer to a project packager, verifier, and compatibility assistant.

## Features

- Interactive CLI with `help`, `wrapper`, `acess`, `test`, `verify`, and `uphash`.
- Project tree scan with `.harbignore` support.
- Stack/runtime detection for Python, Node.js, Go, Rust, Java, Docker, React, Vue, and more.
- Harbor container layout with `Code/` and `Info/`.
- Metadata header with project name, version, OS, architecture, stack list, and tree.
- Recursive `.hash.txt` integrity checks.
- Optional encrypted `.bcb` export.
- Restore encrypted `.bcb` archives back into folders.

## Install

```bash
git clone <repo-url>
cd Harbor
python -m pip install pathspec
```

Harbor uses only the Python standard library plus `pathspec`.

## Run

```bash
python main.py
```

Then use the interactive prompt:

```text
Harbor > help
```

## Commands

```text
help                  Show available commands
exit                  Exit Harbor
clear                 Clear the terminal

wrapper <path>        Create a Harbor container from a project
acess <file> <out>    Restore an encrypted .bcb container
test <path>           Check OS, architecture, and runtime compatibility
verify <path>         Verify container hashes
uphash <path>         Recalculate container hashes
```

`wrapper <path>` defaults to the current directory when no path is provided.

## Container Output

For a project named `MyApp`, Harbor creates:

```text
MyApp-[HARBOR]/
├── Code/             copied project files
├── Info/             header.json, tree.json, .harbignore
└── .hash.txt         root integrity hash
```

If encryption is enabled, Harbor also creates:

```text
MyApp-[HARBOR]_encrypted.bcb
```

## Ignore Rules

Add a `.harbignore` file to the project root to exclude files or folders from the container.

Harbor reads the file using gitwildmatch-style rules through `pathspec`.

Example:

```gitignore
.git/
__pycache__/
node_modules/
*.log
```

## Security Note

Harbor includes a custom educational encryption layer for `.bcb` files. Use it for project packaging and controlled sharing, not as a replacement for audited production cryptography.

We are working to change to AES.

## Project Structure

```text
.
├── main.py                           interactive Harbor CLI
├── imgs/                             project artwork
└── ContainerStuff/
    ├── wrapper.py                    create, hash, verify, and encrypt containers
    ├── acess.py                      restore encrypted containers
    ├── test.py                       compatibility checks
    ├── dirtrain.py                   tree scan and stack detection
    ├── header.py                     metadata header generation
    ├── stack.py                      known stack definitions
    └── Obsidian/BaseSystem/
        ├── crypto.py                 Harbor cipher functions
        ├── hasher.py                 hash helpers
        └── main.py                   base crypto flow
```

## License

MIT License.

Built and maintained by ByKurebo.
