from pathlib import Path

HARBORMAP_PRESET = """project: [YOUR PROJECT NAME]
description: [YOUR PROJECT DESCRIPTION]

variants:
  - type: .harb
    path: any/
    version:
    os: Any
    architecture: Any
    runtime: 

  - type: .harb
    path: linux/
    version:
    os: linux
    architecture:
    runtime: 


  - type: .harb
    path: mac/
    version:
    os: macos
    architecture:
    runtime: 

  - type: .harb
    path: windows/
    version:
    os: windows
    architecture:
    runtime: 

  - type: url
    url: https://
    command:
    version:
    os:
    architecture:
    runtime: 


"""

README_PRESET = """#### Install with [Harbor](https://github.com/kauanmezavila/harbor)
```bash
$ harbor install [HERE GOES YOUR NAME + REPO]@latest
```
"""

HARBINSTALL_PRESET = """hrb:> shell-mode on
hrb:> err-break on

echo Starting installation, please wait...
"""

STRUCTURE = {
    "HarborSpecs": {
        "HarborMap.yaml": HARBORMAP_PRESET,
        "any": {},
        "linux": {},
        "mac": {},
        "windows": {},
    },
    "README.md": README_PRESET,
    ".harbinstall": HARBINSTALL_PRESET,
    ".gitignore": "",
}

def init_project(root: Path) -> None:
    create_tree(root, STRUCTURE)

def create_tree(parent: Path, children: dict) -> None:
    parent.mkdir(parents=True, exist_ok=True)

    for name, content in children.items():
        path = parent / name

        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            create_tree(path, content)
        elif not path.exists():
            path.write_text(content, encoding="utf-8")
