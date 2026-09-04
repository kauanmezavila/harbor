# Upcoming!

## v1.3.0

I will add the, probably, main feature: the download and Github integration

# Updates

## v1.2.1

Harbor now is installer by pyproject.toml and can be used globaly

.harbinstall was created

Fixed and bug on .harignore and fixed the missing cryptography module on requirement.txt

## v1.2.0

Harbor now has a cleaner command-based CLI and a complete container flow:

- `wrapper` creates a Harbor folder, writes metadata, copies project files, hashes the container, and exports `.harb`.
- `inflate` extracts `.harb` containers back into folders.
- `restore` decrypts password-protected `.bcb` exports.
- `verify` checks saved `.hash.txt` files against the current container contents.
- `uphash` refreshes hashes after intentional edits.
- `compatibility` checks OS, architecture, and runtime requirements from `Info/header.json`.

## Documentation

- Updated the English README with the current CLI commands and output names.
- Updated the Portuguese README to match the current code and file structure.
- Replaced old interactive-command references with the current `python main.py <command>` usage.
