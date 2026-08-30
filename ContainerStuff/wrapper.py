import argparse
import hashlib
import os
import shutil
from pathlib import Path
from typing import Optional

import pathspec

from ContainerStuff.header import header
from ContainerStuff.Obsidian.BaseSystem.crypto import (
    BCB_Cryptography_bytes_passwd,
    BCB_bytes_text,
)


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

NOME_HASH = ".hash.txt"


def obter_diretorio() -> Path:
    """Read and validate the project directory from CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Analyse a project path."
    )

    parser.add_argument(
        "diretorio",
        nargs="?",
        default=".",
        help="Path to the project directory (default: current directory).",
    )

    args = parser.parse_args()
    caminho = Path(args.diretorio).expanduser().resolve()

    if not caminho.exists():
        parser.error(
            f"[{RED}ERRO{RESET}] The path does not exist: {caminho}!"
        )

    if not caminho.is_dir():
        parser.error(
            f"[{RED}ERRO{RESET}] The path is not a directory: {caminho}!"
        )

    print(
        f"[{GREEN} OK {RESET}] Project found: [{caminho}]"
    )

    return caminho


def criar_container(nome_container: str, diretorio: Path) -> Path:
    """Create the Harbor container with Code and Info directories."""
    container_path = diretorio.parent / nome_container

    if container_path.exists():
        print(
            f"\n[{YELLOW}INFO{RESET}] Container already exists:"
        )
        print(f"  {container_path}")

        resposta = input(
            "\n[!] Want to overwrite? [y/N]: "
        ).strip().lower()

        if resposta != "y":
            print(
                f"[{YELLOW}INFO{RESET}] Operation cancelled."
            )
            raise SystemExit(0)

        print(
            f"[{YELLOW}INFO{RESET}] Removing old container..."
        )

        if container_path.is_dir():
            shutil.rmtree(container_path)
        else:
            container_path.unlink()

    container_path.mkdir(parents=True, exist_ok=True)
    (container_path / "Code").mkdir(exist_ok=True)
    (container_path / "Info").mkdir(exist_ok=True)

    print(
        f"[{GREEN} OK {RESET}] Container created: {container_path}"
    )

    return container_path


def carregar_ignore(
    diretorio: Path,
    default: Optional[Path] = None,
) -> Optional[pathspec.PathSpec]:
    """Choose and load .harbignore rules for the copy step."""
    project_ignore = diretorio / ".harbignore"

    default_ignore = (
        Path(default)
        if default is not None
        else Path(__file__).resolve().parent / ".harbignore"
    )

    if project_ignore.is_file():
        print(
            f"\n[{CYAN}IGNORE{RESET}] Project .harbignore found:"
        )
        print(f"  {project_ignore}")

        resposta = input(
            "\n[?] Use project .harbignore? [Y/n]: "
        ).strip().lower()

        if resposta in ("", "y", "yes"):
            ignore_path = project_ignore

        elif default_ignore.is_file():
            resposta = input(
                "\n[?] Use default Harbor .harbignore? [Y/n]: "
            ).strip().lower()

            if resposta in ("", "y", "yes"):
                ignore_path = default_ignore

            else:
                print(
                    f"[{YELLOW}INFO{RESET}] "
                    "No ignore file will be used."
                )
                return None

        else:
            print(
                f"[{YELLOW}INFO{RESET}] "
                "No default .harbignore found."
            )
            return None

    else:
        if not default_ignore.is_file():
            print(
                f"[{YELLOW}INFO{RESET}] "
                "No .harbignore found."
            )
            return None

        print(
            f"\n[{CYAN}IGNORE{RESET}] "
            "Default Harbor .harbignore found:"
        )
        print(f"  {default_ignore}")

        resposta = input(
            "\n[?] Use default Harbor .harbignore? [Y/n]: "
        ).strip().lower()

        if resposta in ("", "y", "yes"):
            ignore_path = default_ignore

        else:
            print(
                f"[{YELLOW}INFO{RESET}] "
                "No ignore file will be used."
            )
            return None

    with ignore_path.open("r", encoding="utf-8") as arquivo:
        linhas = [
            linha.strip()
            for linha in arquivo
            if linha.strip()
            and not linha.lstrip().startswith("#")
        ]

    if not linhas:
        print(
            f"[{YELLOW}INFO{RESET}] Ignore file is empty."
        )
        return None

    print(
        f"[{GREEN} OK {RESET}] "
        f"Using ignore file: {ignore_path}"
    )

    return pathspec.PathSpec.from_lines(
        "gitwildmatch",
        linhas,
    )


def copiar_projeto(origem: Path, destino: Path) -> bool:
    """Copy project files into Code and root metadata files into Info."""
    origem = origem.expanduser().resolve()
    destino = destino.expanduser().resolve()

    arquivos_info = {
        "header.json",
        "tree.json",
        ".harbignore",
    }

    if not origem.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERRO{RESET}] Origin not found: {origem}"
        )

    if not origem.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERRO{RESET}] "
            f"The origin is not a directory: {origem}"
        )

    if destino == origem:
        raise ValueError(
            f"\n[{RED}ERRO{RESET}] "
            "The destination cannot be the origin."
        )

    try:
        destino.relative_to(origem)

    except ValueError:
        pass

    else:
        raise ValueError(
            f"\n[{RED}ERRO{RESET}] "
            f"The destination cannot be inside "
            f"the origin: {destino}"
        )

    destino.mkdir(parents=True, exist_ok=True)

    destino_info = destino.parent / "Info"
    destino_info.mkdir(parents=True, exist_ok=True)

    ignore = carregar_ignore(origem)

    print()
    print(f"[{BOLD} MAKE {RESET}] {origem}")
    print("       V")
    print(f"[{BOLD} CODE {RESET}] {destino}")
    print(f"[{BOLD} INFO {RESET}] {destino_info}")
    print()

    copiados = 0
    ignorados = 0
    infos = 0

    for raiz, pastas, arquivos in os.walk(origem):
        raiz = Path(raiz)
        relativo = raiz.relative_to(origem)

        pastas_validas = []

        for pasta in pastas:
            caminho = raiz / pasta
            caminho_relativo = (
                caminho.relative_to(origem).as_posix()
            )
            caminho_para_ignore = caminho_relativo + "/"

            if ignore and ignore.match_file(
                caminho_para_ignore
            ):
                ignorados += 1

                print(
                    f"[{YELLOW} IGNORE {RESET}] "
                    f"{caminho_para_ignore}"
                )

                continue

            pastas_validas.append(pasta)

        # Update os.walk in place so ignored folders are not visited.
        pastas[:] = pastas_validas

        destino_raiz = destino / relativo
        destino_raiz.mkdir(
            parents=True,
            exist_ok=True,
        )

        for arquivo in arquivos:
            origem_arquivo = raiz / arquivo

            relativo_arquivo = (
                origem_arquivo.relative_to(origem)
            )

            relativo_str = relativo_arquivo.as_posix()

            if ignore and ignore.match_file(
                relativo_str
            ):
                ignorados += 1

                print(
                    f"[{YELLOW} IGNORE {RESET}] "
                    f"{relativo_str}"
                )

                continue

            if (
                relativo_arquivo.parent == Path(".")
                and arquivo in arquivos_info
            ):
                shutil.copy2(
                    origem_arquivo,
                    destino_info / arquivo,
                )

                infos += 1

                print(
                    f"[{CYAN}  INFO  {RESET}] "
                    f"{relativo_str}"
                )

                continue

            destino_arquivo = (
                destino / relativo_arquivo
            )

            destino_arquivo.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                origem_arquivo,
                destino_arquivo,
            )

            copiados += 1

            print(
                f"[{GREEN}  CODE  {RESET}] "
                f"{relativo_str}"
            )

    print()
    print(
        f"[{GREEN} OK {RESET}] "
        "Project copied successfully."
    )
    print(f"      Files copied : {copiados}")
    print(f"      Info files   : {infos}")
    print(f"      Items ignored: {ignorados}")
    print(f"      Code         : {destino}")
    print(f"      Info         : {destino_info}")
    print()

    return True


def hash_arquivo(arquivo):
    """Return the SHA-256 hash for one file."""
    sha256 = hashlib.sha256()

    with open(arquivo, "rb") as f:
        for bloco in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            sha256.update(bloco)

    return sha256.hexdigest()


def hash_pasta(pasta, gravar=True):
    """
    Calculate a recursive SHA-256 hash for a folder.

    .hash.txt files are always ignored.

    The hash of a folder depends on:
    - the names and hashes of its files;
    - the names and hashes of its subdirectories.

    If gravar=True, the resulting hash is written to
    <folder>/.hash.txt.
    """
    pasta = Path(pasta)
    itens = []

    for item in sorted(
        pasta.iterdir(),
        key=lambda x: x.name,
    ):
        # Never include hash files in the hash calculation.
        if item.name == NOME_HASH:
            continue

        if item.is_file():
            hash_item = hash_arquivo(item)

            itens.append(
                f"FILE:{item.name}:{hash_item}"
            )

        elif item.is_dir():
            hash_item = hash_pasta(
                item,
                gravar=gravar,
            )

            itens.append(
                f"DIR:{item.name}:{hash_item}"
            )

    dados = "\n".join(itens).encode("utf-8")

    hash_pasta_atual = hashlib.sha256(
        dados
    ).hexdigest()

    if gravar:
        arquivo_hash = pasta / NOME_HASH

        with open(
            arquivo_hash,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(hash_pasta_atual)

    return hash_pasta_atual

def update_hash(container):
    """
    Recalculate and rewrite the complete hash tree.
    """

    container = (
        Path(container)
        .expanduser()
        .resolve()
    )

    if not container.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERRO{RESET}] "
            f"Container not found: {container}"
        )

    if not container.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERRO{RESET}] "
            f"Container path is not a directory: {container}"
        )

    print(
        f"\n[{YELLOW}UPDATE HASH{RESET}] "
        "Updating integrity hashes..."
    )

    hash_raiz = hash_pasta(
        container,
        gravar=True,
    )

    print(
        f"[{GREEN} OK {RESET}] "
        "Integrity hashes updated."
    )

    print(
        f"      Root hash: "
        f"{YELLOW}{hash_raiz}{RESET}\n"
    )

    return hash_raiz

def verify(container):
    """
    Verify the complete hash tree without rewriting hashes.

    Checks:
    1. The current root hash against the saved root hash.
    2. Every .hash.txt against the current hash of its folder.
    3. Which folders have compatible/incompatible hashes.
    4. Repeated saved hash values.
    """
    container = (
        Path(container)
        .expanduser()
        .resolve()
    )

    if not container.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERRO{RESET}] "
            f"Container not found: {container}"
        )

    if not container.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERRO{RESET}] "
            "Container path is not a directory: "
            f"{container}"
        )

    # ---------------------------------------------------------
    # 1. Find every saved hash.
    # ---------------------------------------------------------

    arquivos_hash = sorted(
        container.rglob(NOME_HASH)
    )

    if not arquivos_hash:
        print(
            f"[{RED}VERIFY{RESET}] "
            "No .hash.txt files were found."
        )

        return {
            "integridade_raiz": False,
            "hashes_encontrados": 0,
            "hashes_compativeis": 0,
            "hashes_incompativeis": 0,
            "hashes_repetidos": 0,
            "hashes_unicos": 0,
            "resultados": [],
        }

    # ---------------------------------------------------------
    # 2. Calculate the current root hash.
    #
    # hash_pasta ignores every .hash.txt, so this represents
    # the current content of the entire container.
    # ---------------------------------------------------------

    hash_raiz_atual = hash_pasta(
        container,
        gravar=False,
    )

    # ---------------------------------------------------------
    # 3. Read the saved root hash.
    # ---------------------------------------------------------

    arquivo_hash_raiz = (
        container / NOME_HASH
    )

    hash_raiz_salvo = None

    if arquivo_hash_raiz.is_file():
        hash_raiz_salvo = (
            arquivo_hash_raiz
            .read_text(encoding="utf-8")
            .strip()
        )

    integridade_raiz = (
        hash_raiz_salvo is not None
        and hash_raiz_salvo == hash_raiz_atual
    )

    # ---------------------------------------------------------
    # 4. Verify every .hash.txt against its own folder.
    # ---------------------------------------------------------

    resultados = []

    for arquivo_hash in arquivos_hash:
        pasta = arquivo_hash.parent

        hash_salvo = (
            arquivo_hash
            .read_text(encoding="utf-8")
            .strip()
        )

        hash_atual = hash_pasta(
            pasta,
            gravar=False,
        )

        compativel = (
            hash_salvo == hash_atual
        )

        try:
            caminho_relativo = (
                arquivo_hash.relative_to(container)
            )
        except ValueError:
            caminho_relativo = arquivo_hash

        resultados.append(
            {
                "arquivo_hash": arquivo_hash,
                "pasta": pasta,
                "caminho_relativo": caminho_relativo,
                "hash_salvo": hash_salvo,
                "hash_atual": hash_atual,
                "compativel": compativel,
            }
        )

    # ---------------------------------------------------------
    # 5. Statistics.
    # ---------------------------------------------------------

    hashes_compativeis = sum(
        resultado["compativel"]
        for resultado in resultados
    )

    hashes_incompativeis = (
        len(resultados)
        - hashes_compativeis
    )

    valores = [
        resultado["hash_salvo"]
        for resultado in resultados
    ]

    hashes_unicos = len(set(valores))

    hashes_repetidos = (
        len(valores)
        - hashes_unicos
    )

    # ---------------------------------------------------------
    # 6. Display root verification.
    # ---------------------------------------------------------

    print()
    print(
        f"[{BOLD}{CYAN}VERIFY{RESET}] "
        f"Container: {container}"
    )

    print()

    print(
        f"      Root hash saved   : "
        f"{YELLOW}{hash_raiz_salvo}{RESET}"
    )

    print(
        f"      Root hash current : "
        f"{YELLOW}{hash_raiz_atual}{RESET}"
    )

    if integridade_raiz:
        print(
            f"      Root integrity    : "
            f"{GREEN}VALID{RESET}"
        )
    else:
        print(
            f"      Root integrity    : "
            f"{RED}INVALID{RESET}"
        )

    # ---------------------------------------------------------
    # 7. Display each .hash.txt verification.
    # ---------------------------------------------------------

    print()

    for resultado in resultados:
        caminho = resultado["caminho_relativo"]

        if resultado["compativel"]:
            status = f"{GREEN}VALID{RESET}"
        else:
            status = f"{RED}INVALID{RESET}"

        print(
            f"      [{status}] "
            f"{caminho}"
        )

        if not resultado["compativel"]:
            print(
                f"          Saved : "
                f"{resultado['hash_salvo']}"
            )

            print(
                f"          Actual: "
                f"{resultado['hash_atual']}"
            )

    # ---------------------------------------------------------
    # 8. Summary.
    # ---------------------------------------------------------

    print()

    print(
        f"      Hashes on project     : "
        f"{len(arquivos_hash)}"
    )

    print(
        f"      Compatible hashes     : "
        f"{GREEN}{hashes_compativeis}{RESET}"
    )

    print(
        f"      Incompatible hashes   : "
        f"{RED}{hashes_incompativeis}{RESET}"
    )

    print(
        f"      Repeated saved hashes : "
        f"{hashes_repetidos}"
    )

    print(
        f"      Unique saved hashes   : "
        f"{hashes_unicos}"
    )

    print()

    # ---------------------------------------------------------
    # 9. Final integrity conclusion.
    # ---------------------------------------------------------

    projeto_integro = (
        integridade_raiz
        and hashes_incompativeis == 0
    )

    if projeto_integro:
        print(
            f"[{GREEN} OK {RESET}] "
            "Container integrity verified."
        )
    else:
        print(
            f"[{RED}ERRO{RESET}] "
            "Container integrity check failed."
        )

    print()

    return {
        "hash_raiz_salvo": hash_raiz_salvo,
        "hash_raiz_atual": hash_raiz_atual,
        "integridade_raiz": integridade_raiz,
        "projeto_integro": projeto_integro,
        "hashes_encontrados": len(arquivos_hash),
        "hashes_compativeis": hashes_compativeis,
        "hashes_incompativeis": hashes_incompativeis,
        "hashes_repetidos": hashes_repetidos,
        "hashes_unicos": hashes_unicos,
        "resultados": resultados,
    }


def main_wrapper(path: Optional[Path] = None) -> None:
    """Create a Harbor container for a project directory."""
    diretorio = (
        path
        if path
        else obter_diretorio()
    )

    diretorio = (
        Path(diretorio)
        .expanduser()
        .resolve()
    )

    if not diretorio.exists():
        raise FileNotFoundError(
            f"\n[{RED}ERRO{RESET}] "
            f"Project directory not found: {diretorio}"
        )

    if not diretorio.is_dir():
        raise NotADirectoryError(
            f"\n[{RED}ERRO{RESET}] "
            f"Project path is not a directory: {diretorio}"
        )

    project_name = header(diretorio)

    if not project_name:
        raise ValueError(
            f"\n[{RED}ERRO{RESET}] "
            "Could not determine the project name."
        )

    container = criar_container(
        project_name,
        diretorio,
    )

    code_path = container / "Code"

    copiar_projeto(
        diretorio,
        code_path,
    )

    # Creates the complete recursive hash tree.
    hash_code = hash_pasta(container)

    criar = input(
        "\n[?] Create encrypted copy of the container? [Y/n]: "
    )

    criar = criar.strip().lower()

    if criar in ("", "y", "yes"):
        senha = input(
            "\n[?] Enter a password for encryption: "
        ).strip()

        if not senha:
            print(
                f"[{YELLOW}INFO{RESET}] "
                "No password provided. Skipping encryption."
            )
            return

        arquivo_zip = (
            container.parent
            / f"{project_name}.zip"
        )

        shutil.make_archive(
            str(arquivo_zip.with_suffix("")),
            "zip",
            container,
        )

        container_bytes = BCB_bytes_text(
            arquivo_zip
        )

        arquivo_saida = (
            container.parent
            / f"{project_name}_encrypted.bcb"
        )

        conteudo_criptografado = (
            BCB_Cryptography_bytes_passwd(
                container_bytes,
                senha,
            )
        )

        with open(
            arquivo_saida,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(conteudo_criptografado)

        arquivo_zip.unlink()

        print(
            f"[{GREEN} OK {RESET}] "
            f"Encrypted copy created: {arquivo_saida}"
        )

    print(
        f"\n[{GREEN} OK {RESET}] "
        "Container creation completed successfully on: "
        f"\n>>>  {container}"
        f"\n\nHash: {YELLOW}{hash_code}{RESET}\n"
    )


if __name__ == "__main__":
    main_wrapper()