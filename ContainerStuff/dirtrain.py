import json
import os
from pathlib import Path

import pathspec

from ContainerStuff.stack import STACKS

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


def c(text: str, color: str) -> str:
    """Wrap text in an ANSI color sequence."""
    return f"{color}{text}{RESET}"


def titulo(texto: str):
    """Print a compact section title."""
    largura = 64

    print()
    print(c("//" + "=" * largura + r"\\", CYAN))
    print(c("||", CYAN) + f"  {texto:<{largura - 2}}" + c("||", CYAN))
    print(c(r"\\" + "=" * largura + "//", CYAN))
    print()


def linha():
    """Print a visual divider."""
    print(c("--" * 64, GRAY))


class StackDetector:
    """Detect project stacks from known file, extension, and folder names."""

    def __init__(self):
        self.detected = {}

    def detect(self, name: str, is_file: bool):
        if is_file and name in STACKS.get("files", {}):
            return STACKS["files"][name]["stack"]

        if is_file:
            ext = Path(name).suffix
            if ext in STACKS.get("extensions", {}):
                return STACKS["extensions"][ext]["stack"]

        if not is_file and name in STACKS.get("folders", {}):
            return STACKS["folders"][name]

        return None

    def add_stack(self, stack: str, path: str):
        self.detected.setdefault(stack, []).append(path)


def buscar_runtime(stack: str):
    """Find the first runtime declared for a detected stack."""
    for category in ("extensions", "files"):
        for data in STACKS.get(category, {}).values():
            if not isinstance(data, dict):
                continue

            if data.get("stack") != stack:
                continue

            if "runtime" in data:
                return data["runtime"]

            if "required" in data and data["required"]:
                return data["required"][0]

    return None


def carregar_ignore(diretorio: str):
    """Load .harbignore rules from a scanned directory."""
    ignore_path = os.path.join(diretorio, ".harbignore")

    if not os.path.isfile(ignore_path):
        return None

    with open(ignore_path, "r", encoding="utf-8") as f:
        linhas = [
            linha.strip()
            for linha in f.readlines()
            if linha.strip() and not linha.lstrip().startswith("#")
        ]

    if not linhas:
        return None

    return pathspec.PathSpec.from_lines("gitwildmatch", linhas)


def mapear_diretorio(
    diretorio: str,
    salvar_json: bool = True,
    json_path: str = "tree.json",
):
    """Map a directory tree and collect stack detection details."""
    detector = StackDetector()
    diretorio = os.path.abspath(diretorio)
    ignore = carregar_ignore(diretorio)
    stats = {"files": 0, "folders": 0, "ignored": 0}

    def ignorado(caminho: str):
        if ignore is None:
            return False

        relativo = os.path.relpath(caminho, diretorio).replace(os.sep, "/")
        return ignore.match_file(relativo)

    def construir(caminho: str):
        tree = {}

        try:
            itens = sorted(os.listdir(caminho), key=lambda x: x.lower())
        except PermissionError:
            print(c(f" ! No permission: {caminho}", YELLOW))
            return tree

        for item in itens:
            caminho_item = os.path.join(caminho, item)

            if ignorado(caminho_item):
                stats["ignored"] += 1
                relativo = os.path.relpath(caminho_item, diretorio)
                print(c(f"  > ignored  {relativo}", GRAY))
                continue

            if os.path.isdir(caminho_item):
                stats["folders"] += 1
                stack = detector.detect(item, False)

                if stack:
                    detector.add_stack(stack, caminho_item)

                tree[item] = construir(caminho_item)
                continue

            stats["files"] += 1
            stack = detector.detect(item, True)

            if stack:
                detector.add_stack(stack, caminho_item)

            tree[item] = None

        return tree

    nome_raiz = os.path.basename(diretorio)
    print(c(f"  {c('>', GREEN)} Analising {c(nome_raiz, WHITE)}...", WHITE))

    tree = {nome_raiz: construir(diretorio)}

    if salvar_json:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(tree, f, indent=4, ensure_ascii=False)

    return tree, detector.detected, stats


def mostrar_tree(tree: dict):
    """Print the mapped project tree."""
    titulo("PROJECT TREE")

    def imprimir(no: dict, prefixo=""):
        itens = list(no.items())

        for i, (nome, conteudo) in enumerate(itens):
            ultimo = i == len(itens) - 1
            conector = "└── " if ultimo else "├── "

            if isinstance(conteudo, dict):
                print(prefixo + c(conector, CYAN) + c("/", BLUE) + c(nome, WHITE))
                imprimir(conteudo, prefixo + ("    " if ultimo else "│   "))
                continue

            extensao = Path(nome).suffix
            icone = "" if extensao else ":"
            cor = WHITE if extensao else GRAY
            print(prefixo + c(conector, GRAY) + c(f"{icone} ", CYAN) + c(nome, cor))

    raiz, conteudo = next(iter(tree.items()))
    print(c("> ", MAGENTA) + c(raiz, BOLD + WHITE))
    imprimir(conteudo)


def mostrar_stacks(stacks: dict, stats: dict | None = None):
    """Print detected stacks and return their runtime list."""
    titulo("DETECTED STACKS")
    stack_list: list[str] = []

    if not stacks:
        print(c("  ! No stacks detected.", YELLOW))
        return stack_list

    total = len(stacks)
    plural = "s" if total != 1 else ""

    print(c(f"  {total} stack{plural} detected", GRAY))
    print()

    for index, (stack, paths) in enumerate(sorted(stacks.items())):
        ultimo = index == len(stacks) - 1
        runtime = buscar_runtime(stack)

        if runtime and runtime not in stack_list:
            stack_list.append(runtime)

        print(c("└── " if ultimo else "├── ", GRAY) + c("◆ ", GREEN) + c(stack, BOLD + WHITE))

        if runtime:
            print(c("    ├── runtime: ", GRAY) + c(runtime, CYAN))

        for path_index, path in enumerate(paths):
            ultimo_path = path_index == len(paths) - 1

            if ultimo:
                prefixo = "    └── " if ultimo_path else "    ├── "
            else:
                prefixo = "│   └── " if ultimo_path else "│   ├── "

            print(c(prefixo, GRAY) + c(os.path.normpath(path), DIM + WHITE))

        print(c("│", GRAY) if not ultimo else "")

    return stack_list


def mostrar_resumo(stats: dict, stacks: dict, stack_list: list[str]):
    """Print scan totals."""
    titulo("SCAN SUMMARY")

    total_stacks = len(stacks)
    print(f"  {c('FILES', CYAN):<20}{stats['files']}")
    print(f"  {c('FOLDERS', CYAN):<20}{stats['folders']}")
    print(f"  {c('IGNORED', CYAN):<20}{stats['ignored']}")
    print(f"  {c('STACKS', CYAN):<20}{total_stacks}")
    print(f"  {c('RUNTIMES', CYAN):<20}{len(stack_list)}")
    print()


def main_dirtrain(diretorio: str):
    """Scan a project and return its tree plus detected runtimes."""
    titulo("HARBOR <SCAN>")

    print(c("  Target  ", GRAY) + c(os.path.abspath(diretorio), WHITE))
    print()

    tree, stacks, stats = mapear_diretorio(diretorio)
    mostrar_tree(tree)
    stack_list = mostrar_stacks(stacks, stats)
    mostrar_resumo(stats, stacks, stack_list)

    print(c("OK Scan concluded.", GREEN))
    print()

    return tree, stack_list
