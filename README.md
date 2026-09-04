<p align="center">
  <img src="imgs/HarborBanner.png" alt="Harbor logo">
</p>

<h1 align="center">Harbor</h1>

<p align="center">
  A lightweight open-source CLI for packaging projects into portable Harbor containers with metadata, compatibility checks, integrity hashes, and optional encrypted exports.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-111111?style=for-the-badge">
  <img alt="Status" src="https://img.shields.io/badge/Status-v1.0.0-9b59b6?style=for-the-badge">
</p>

---

## What is Harbor?

Harbor turns a project folder into a portable container-like package.

It scans the project tree, detects known stacks, writes metadata, copies code into a clean `Code/` area, stores root files in `Info/`, creates recursive SHA-256 integrity hashes, compresses the result as a `.harb` file, and can also create a password-encrypted `.bcb` export.

Harbor is not Docker. It is closer to a project packager, verifier, and compatibility assistant.

## Features

- `wrapper`: create a Harbor container from a project directory.
- `inflate`: extract a `.harb` container.
- `restore`: decrypt and extract an encrypted `.bcb` export.
- `verify`: validate the recursive `.hash.txt` integrity tree.
- `uphash`: recalculate container hashes after intentional changes.
- `compatibility`: check the current OS, architecture, and runtimes against container metadata.
- `.harbignore` support with gitwildmatch-style rules.
- `run`: runs an `.harbinstall`, a installing script
- Stack detection for Python, Node.js, Go, Rust, Java, Docker, React, Vue, and more.

## Install

```bash
git clone https://github.com/kauanmezavila/harbor.git
cd Harbor
```

Now choose the most adequate method:
```bash
pip install .
python -m pip install .
pipx install .
```
(Note: we use pyproject.toml to habilite the global command)

## Usage

```bash
harbor <command> <args>
```

```text
Commands:
  wrapper <path>                            Create a Harbor container
  inflate <file.harb> [--out <directory>]   Extract a .harb container
  restore <file.bcb> --password <password>  Restore an encrypted .bcb export
  verify <path>                             Verify container hashes
  uphash <path>                             Recalculate container hashes
  compatibility <path>                      Check container compatibility
  run <path>                                Runs the .harbinstall
```

Examples:

```bash
harbor wrapper MyApp
harbor inflate "MyApp-Any-Any-[HARBOR].harb" --out ./restored
harbor restore "MyApp-Any-Any-[HARBOR]_encrypted.bcb" --password "secret" --out ./restored
harbor verify "MyApp-Any-Any-[HARBOR]"
harbor compatibility "MyApp-Any-Any-[HARBOR]"
harbor install "MyApp-Any-Any-[HARBOR]"
```
Note: for security reasons, install will may only run .harbinstall when runned in the project root dir

## Container Output

For a project named `MyApp`, Harbor creates:

```text
MyApp-Any-Any-[HARBOR]/
├── Code/             copied project files
├── Info/             header.json, tree.json, .harbignore, .harbinstall
└── .hash.txt         root integrity hash
```

It also creates:

```text
MyApp-Any-Any-[HARBOR].harb
```

If encryption is enabled, Harbor creates:

```text
MyApp-Any-Any-[HARBOR]_encrypted.bcb
```

The `Any-Any` part changes when you set specific architectures or operating systems during wrapping.

## Ignore Rules

Add a `.harbignore` file to the project root to exclude files or folders from the container. Just like an .gitignore

Example:

```gitignore
.git/
__pycache__/
node_modules/
*.log
```

## .harbinstall

In 1.2.1 we now have the amazing .harbinstall: an file that helps the installation using subprocess.

To be able to run you need:
- 1: Create the installation file just like an .sh/.bat (Remebers it runs LINE by LINE)
- 2: Add one of the index `hrb:> ` and HARB-IMG commands if you want!:
```bash
shell-mode  : run commands with the shell or subprocess list [Starts on 'True']
output      : capture the output [Starts on 'False']
err-break   : determinates if the HARB-IMG needs to stop or not if an error occurs [Starts on 'False']
usr-log     : shows the logs of HARB-IMG for the user [Starts on 'True']
```
Note: if you not write an .harbinstall on the root dir, Harbo will push an empty one on the container Info folder

## Security Note

Encrypted `.bcb` exports use AES-GCM through the `cryptography` package. Use them for packaging and controlled sharing, not as a replacement for a full audited production security process.

## Project Structure

```text
.
├── ContainerStuff          
│   ├── access.py
│   ├── compatibility.py
│   ├── dirtrain.py
│   ├── header.py
│   ├── Obsidian
│   │   └── BaseSystem
│   │       ├── crypto.py
│   │       ├── hasher.py
│   │       └── main.py
│   ├── runinstall.py
│   ├── stack.py
│   ├── wrapper.py
│   └── WrapperStuff
│       ├── containerflux.py
│       ├── hashflux.py
│       └── verifyflux.py
├── Dumpster
│   ├── main-cli.py
│   └── README.md
├── imgs
│   ├── Harbor2.png
│   ├── HarborBanner.png
│   └── Harbor.png
├── main.py
├── OfficeStuff
├── pyproject.toml
├── README.md
├── README.pt-BR.md
├── requirements.txt
└── UPDATES.md
```

## License

MIT License.

Built and maintained by ByKurebo.
