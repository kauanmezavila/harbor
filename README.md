<p align="center">
  <img src="imgs/HarborBanner.png" alt="Harbor logo">
</p>

<h1 align="center">Harbor</h1>

<p align="center">
  A lightweight open-source system that helps developers distribute code and users to download the most compatible by packaging projects into portable Harbor containers with metadata, compatibility checks, integrity hashes, and optional encrypted exports.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-111111?style=for-the-badge">
  <img alt="Status" src="https://img.shields.io/badge/Status-v1.0.0-9b59b6?style=for-the-badge">
</p>

---

## What is Harbor?

Harbor helps developers distribute code and users to download the most compatible

It scans the project tree, detects known stacks, writes metadata, copies code into a clean `Code/` area, stores root files in `Info/`, creates recursive SHA-256 integrity hashes, compresses the result as a `.harb` file, and can also create a password-encrypted `.bcb` export.

Then, the dev can make an HarborSpecs folder with the sources and a HarborMap.yaml that tells the system where to find the right source for the system.

After this, anyone with the harbor CLI can download the most compatible (or other) version in the default or other branch.

Harbor is not Docker. It is closer to a project packager, verifier, and compatibility assistant.

## Features

- `wrapper`: create a Harbor container from a project directory.
- `inflate`: extract a `.harb` container.
- `restore`: decrypt and extract an encrypted `.bcb` export.
- `verify`: validate the recursive `.hash.txt` integrity tree.
- `uphash`: recalculate container hashes after intentional changes.
- `compatibility`: check the current OS, architecture, and runtimes against container metadata.
- `.harbignore` support with gitwildmatch-style rules.
- `run`: runs an `.harbinstall`, a installing script.
- `install`: Install a project from GitHub.
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
pipx install .            <--- i HIGHLY recommend this one
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
  install <username/repo@version> <args>    Install a project from GitHub
```

Examples:

```bash
harbor wrapper MyApp
harbor inflate "MyApp-Any-Any-[HARBOR].harb" --out ./restored
harbor restore "MyApp-Any-Any-[HARBOR]_encrypted.bcb" --password "secret" --out ./restored
harbor verify "MyApp-Any-Any-[HARBOR]"
harbor compatibility "MyApp-Any-Any-[HARBOR]"
harbor run "MyApp-Any-Any-[HARBOR]"
harbor install linus/myapp@latest --branch master
```
Note: for security reasons, `run` will may only run `.harbinstall` when runned in the project root dir

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

## HarborSpecs

In 1.3.0 we added the HarborSpecs, a folder in your project root directory.
In this folder you will put the OS folder, after the version.

An example:

.
├── ContainerStuff
│   ├── access.py
│   ├── compatibility.py
│   ├── dirtrain.py
│   ├── header.py
│   ├── install.py
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
|
├── HarborSpecs                                                <--- Here is HarborSpecs folder
|   ├── HarborMap.yaml                                         <--- Here is the HarborMap file
│   ├── any                                                    <--- In "Any" you put the code that run in ANY OS
│   │   ├── v1.1                                               <--- The version
│   │   │   └── HarborBeacon-Any-Any-[HARBOR].harb             <--- The code source
│   │   └── v1.2
│   │       └── HarborBeacon-Any-Any-[HARBOR].harb
│   ├── linux
│   │   ├── v1.0
│   │   │   └── HarborBeacon-x86_64-linux-[HARBOR].harb
│   │   ├── v1.1
│   │   │   └── HarborBeacon-arm64-linux-[HARBOR].harb
│   │   └── v1.2
│   │       └── HarborBeacon-x86_64-arm64-linux-[HARBOR].harb
│   ├── mac
│   │   └── v1.2
│   │       └── HarborBeacon-arm64-macos-[HARBOR].harb
│   └── windows
│       └── v1.1
│           └── HarborBeacon-x86_64-windows-[HARBOR].harb
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

The only thing here that you actually needs to follow is the folder HarborSpecs be in the root directory and after, the sources

## HarborMap.yaml

This is the HEART of harbor install, in there you can configure some things that will guide the system.

What you NEED to follow to construct:
- Names like:
  - project
  - description
  - variants
  - path
  - version
  - os
  - architecture
  - runtime
- Indentation

An example, if you follow it, your users will have an amazing experience:
```yaml
project: HarborBeacon                                                                        # The project name shown on install menu                                  
description: Same fictional project packaged as HarborSpecs variants by OS, architecture, and version. # The project descritption shown on install menu

variants:                                                           # A list of source variants 'objects'
  - path: any/v1.1/HarborBeacon-Any-Any-[HARBOR].harb               # THE PATH, this is VERY IMPORTANT, consider the path after HarborSpecs
    version: 1.1.0                                                  # Important for the filter
    os: Any                                                         # Important for the filter too
    architecture: Any                                               # Same
    runtime: python>=3.12                                           # Not very important, but is good for the filter

  - path: any/v1.2/HarborBeacon-Any-Any-[HARBOR].harb
    version: 1.2.0
    os: Any
    architecture: Any
    runtime: python>=3.12

  - path: linux/v1.0/HarborBeacon-x86_64-linux-[HARBOR].harb
    version: 1.0.0
    os: linux
    architecture: x86_64
    runtime: python>=3.12

  - path: linux/v1.1/HarborBeacon-arm64-linux-[HARBOR].harb
    version: 1.1.0
    os: linux
    architecture: arm64
    runtime: python>=3.12

  - path: linux/v1.2/HarborBeacon-x86_64-arm64-linux-[HARBOR].harb
    version: 1.2.0
    os: linux
    architecture: x86_64, arm64
    runtime: python>=3.12

  - path: mac/v1.2/HarborBeacon-arm64-macos-[HARBOR].harb
    version: 1.2.0
    os: macos
    architecture: arm64
    runtime: python>=3.12

  - path: windows/v1.1/HarborBeacon-x86_64-windows-[HARBOR].harb
    version: 1.1.0
    os: windows
    architecture: x86_64
    runtime: python>=3.12
```

If you specify the path good, you can organize HarborSpecs in a lots of ways
(For real, ANY way is valid, the only important thing is the HarborMap.yaml having all the nescessary infos)

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
│   ├── install.py
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
├── HarborSpecs
│   ├── any
│   │   ├── v1.1
│   │   │   └── HarborBeacon-Any-Any-[HARBOR].harb
│   │   └── v1.2
│   │       └── HarborBeacon-Any-Any-[HARBOR].harb
│   ├── HarborMap.yaml
│   ├── linux
│   │   ├── v1.0
│   │   │   └── HarborBeacon-x86_64-linux-[HARBOR].harb
│   │   ├── v1.1
│   │   │   └── HarborBeacon-arm64-linux-[HARBOR].harb
│   │   └── v1.2
│   │       └── HarborBeacon-x86_64-arm64-linux-[HARBOR].harb
│   ├── mac
│   │   └── v1.2
│   │       └── HarborBeacon-arm64-macos-[HARBOR].harb
│   └── windows
│       └── v1.1
│           └── HarborBeacon-x86_64-windows-[HARBOR].harb
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
