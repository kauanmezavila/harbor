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
- Stack detection for Python, Node.js, Go, Rust, Java, Docker, React, Vue, and more.

## Install

```bash
git clone https://github.com/kauanmezavila/harbor.git
cd Harbor
python -m pip install pathspec cryptography
```

## Usage

```bash
python main.py <command> <args>
```

```text
Commands:
  wrapper <path>                            Create a Harbor container
  inflate <file.harb> [--out <directory>]   Extract a .harb container
  restore <file.bcb> --password <password>  Restore an encrypted .bcb export
  verify <path>                             Verify container hashes
  uphash <path>                             Recalculate container hashes
  compatibility <path>                      Check container compatibility
```

Examples:

```bash
python main.py wrapper ./MyApp
python main.py inflate "./MyApp-Any-Any-[HARBOR].harb" --out ./restored
python main.py restore "./MyApp-Any-Any-[HARBOR]_encrypted.bcb" --password "secret" --out ./restored
python main.py verify "./MyApp-Any-Any-[HARBOR]"
python main.py compatibility "./MyApp-Any-Any-[HARBOR]"
```

## Container Output

For a project named `MyApp`, Harbor creates:

```text
MyApp-Any-Any-[HARBOR]/
├── Code/             copied project files
├── Info/             header.json, tree.json, .harbignore
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

Add a `.harbignore` file to the project root to exclude files or folders from the container.

Example:

```gitignore
.git/
__pycache__/
node_modules/
*.log
```

## Security Note

Encrypted `.bcb` exports use AES-GCM through the `cryptography` package. Use them for packaging and controlled sharing, not as a replacement for a full audited production security process.

## Project Structure

```text
.
├── main.py                           Harbor command dispatcher
├── imgs/                             project artwork
└── ContainerStuff/
    ├── access.py                     restore encrypted .bcb exports
    ├── compatibility.py              OS, architecture, and runtime checks
    ├── dirtrain.py                   tree scan and stack detection
    ├── header.py                     metadata header generation
    ├── stack.py                      known stack definitions
    ├── wrapper.py                    wrapper, .harb compression, and inflation flow
    ├── WrapperStuff/
    │   ├── containerflux.py          copy files and apply .harbignore
    │   ├── hashflux.py               hash creation and refresh
    │   └── verifyflux.py             hash verification
    └── Obsidian/BaseSystem/
        ├── crypto.py                 Harbor cipher functions
        └── main.py                   base crypto flow
```

## License

MIT License.

Built and maintained by ByKurebo.
