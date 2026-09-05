<p align="center">
  <img src="imgs/HarborBanner.png" alt="Harbor logo">
</p>

<h1 align="center">Harbor</h1>

<p align="center">
  Um sistema leve open-source que ajuda os desenvolvedores a distribuir código e os usuários a baixar o mais compatível, empacotando projetos em contêineres portáteis Harbor com metadados, verificações de compatibilidade, hashes de integridade e exportações criptografadas opcionais.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-111111?style=for-the-badge">
  <img alt="Status" src="https://img.shields.io/badge/Status-v1.0.0-9b59b6?style=for-the-badge">
</p>

---

## O que é o Harbor?

Harbor ajuda os desenvolvedores a distribuir código e os usuários a baixar o mais compatível

Ele verifica a árvore do projeto, detecta stacks conhecidas, grava metadados, copia código em uma área `Code/` limpa, armazena arquivos raiz em `Info/`, cria hashes de integridade SHA-256 recursivos, compacta o resultado como um arquivo `.harb` e também pode criar uma exportação `.bcb` criptografada por senha.

Depois, o desenvolvedor pode criar uma pasta `HarborSpecs` com os códigos-fonte e um `HarborMap.yaml` que informa ao sistema onde encontrar a fonte correta para cada variante.

Depois disso, qualquer pessoa com a CLI do Harbor pode baixar a versão mais compatível (ou qualquer outra) na branch padrão ou em outra branch.

Harbor não é um Docker. Está mais próximo de um empacotador de projeto, verificador e assistente de compatibilidade.

## Funções

- `wrapper`: cria um contêiner Harbor a partir de um diretório de projeto.
- `inflate`: extrai um container `.harb`.
- `restore`: descriptografa e extrai um `.bcb` criptografado.
- `verify`: valida a árvore de integridade recursiva `.hash.txt`.
- `uphash`: recalcula hashes de contêineres após alterações intencionais.
- `compatibility`: verifica o sistema operacional, a arquitetura e os tempos de execução atuais em relação aos metadados do contêiner.
- Suporte a `.harbignore` com regras no estilo gitwildmatch.
- `run`: executa um `.harbinstall`, um script de instalação.
- `install`: Instala um projeto do GitHub.
- Detecção de stack para Python, Node.js, Go, Rust, Java, Docker, React, Vue e muito mais.

## Instalação

```bash
git clone https://github.com/kauanmezavila/harbor.git
cd Harbor
```

Agora escolha o método mais adequado pro seu PC
```bash
pip install .
python -m pip install .
pipx install .            <--- eu recomendo MUITO esse
```
(Nota: usamos pyproject.toml para habilitar o comando global)

## Uso

```bash
harbor <command> <args>
```

```text
Comandos:
  wrapper <path>                            Cria um contêiner Harbor
  inflate <file.harb> [--out <directory>]   Extrai um contêiner .harb
  restore <file.bcb> --password <password>  Restaura uma exportação .bcb criptografada
  verify <path>                             Verifica os hashes do contêiner
  uphash <path>                             Recalcula os hashes do contêiner
  compatibility <path>                      Verifica a compatibilidade do contêiner
  run <path>                                Executa o `.harbinstall`
  install <usuario/repo@versao> <args>      Instala um projeto do GitHub
```

Exemplos:

```bash
harbor wrapper MyApp
harbor inflate "MyApp-Any-Any-[HARBOR].harb" --out ./restored
harbor restore "MyApp-Any-Any-[HARBOR]_encrypted.bcb" --password "secret" --out ./restored
harbor verify "MyApp-Any-Any-[HARBOR]"
harbor compatibility "MyApp-Any-Any-[HARBOR]"
harbor run "MyApp-Any-Any-[HARBOR]"
harbor install linus/myapp@latest --branch master
```
Nota: por motivos de segurança, `run` só deve executar o `.harbinstall` quando for rodado na raiz do projeto.

## Saída Do Contêiner

Para um projeto chamado `MyApp`, o Harbor cria:

```text
MyApp-Any-Any-[HARBOR]/
├── Code/             arquivos copiados do projeto
├── Info/             header.json, tree.json, .harbignore, .harbinstall
└── .hash.txt         hash de integridade raiz
```

Ele também cria:

```text
MyApp-Any-Any-[HARBOR].harb
```

Se a criptografia estiver ativada, o Harbor cria:

```text
MyApp-Any-Any-[HARBOR]_encrypted.bcb
```

A parte `Any-Any` muda quando você define arquiteturas ou sistemas operacionais específicos durante o empacotamento.


## Regras De Ignore

Adicione um arquivo `.harbignore` na raiz do projeto para excluir arquivos ou pastas do contêiner. É como um `.gitignore`.

Exemplo:

```gitignore
.git/
__pycache__/
node_modules/
*.log
```

## HarborSpecs

Na versão 1.3.0, adicionamos o `HarborSpecs`, uma pasta na raiz do projeto.
Nessa pasta você coloca a pasta do sistema operacional, depois da versão.

Um exemplo:

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
├── HarborSpecs                                                <--- Aqui fica a pasta HarborSpecs
|   ├── HarborMap.yaml                                         <--- Aqui fica o arquivo HarborMap
│   ├── any                                                    <--- Em "Any" você coloca o código que roda em QUALQUER OS
│   │   ├── v1.1                                               <--- A versão
│   │   │   └── HarborBeacon-Any-Any-[HARBOR].harb             <--- A fonte do código
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

A única coisa que você realmente precisa seguir aqui é deixar a pasta `HarborSpecs` na raiz do projeto, depois as fontes.

## HarborMap.yaml

Este é o coração do `harbor install`. Nele você configura as informações que vão guiar o sistema.

O que você PRECISA seguir na estrutura:
- Nomes como:
  - project
  - description
  - variants
  - path
  - version
  - os
  - architecture
  - runtime
- Indentação

Um exemplo, se você seguir assim, seus usuários terão uma experiência muito melhor:
```yaml
project: HarborBeacon                                                                        # Nome do projeto mostrado no menu de instalação
description: Same fictional project packaged as HarborSpecs variants by OS, architecture, and version. # Descrição do projeto mostrada no menu de instalação

variants:                                                           # Uma lista de objetos de variante de fonte
  - path: any/v1.1/HarborBeacon-Any-Any-[HARBOR].harb               # O CAMINHO, isso é MUITO IMPORTANTE; considere o caminho depois de HarborSpecs
    version: 1.1.0                                                  # Importante para o filtro
    os: Any                                                         # Importante para o filtro também
    architecture: Any                                               # O mesmo
    runtime: python>=3.12                                           # Não é tão importante, mas ajuda no filtro

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

Se você especificar bem o caminho, dá para organizar o `HarborSpecs` de várias formas.
(Qualquer forma é válida na verdade, o que realmente importa é o HarborMap.yaml indicar todas as infos)

## .harbinstall

Na versão 1.2.1, o Harbor passou a ter suporte ao `.harbinstall`: um arquivo que ajuda na instalação usando `subprocess`.

Para usar:
- 1: Crie o arquivo de instalação como faria com um `.sh` ou `.bat`. Lembre-se de que ele roda linha por linha.
- 2: Adicione o prefixo `hrb:> ` e comandos HARB-IMG se quiser:
```bash
shell-mode  : executa comandos com shell ou lista de subprocessos [começa como 'True']
output      : captura a saída [começa como 'False']
err-break   : define se o HARB-IMG deve parar quando ocorrer um erro [começa como 'False']
usr-log     : mostra os logs do HARB-IMG para o usuário [começa como 'True']
```
Nota: se você não escrever um `.harbinstall` na raiz, o Harbor colocará um vazio na pasta `Info` do contêiner.

## Nota De Segurança

Exportações `.bcb` criptografadas usam AES-GCM através do pacote `cryptography`. Use-as para empacotamento e compartilhamento controlado, não como substituto de um processo de segurança de produção completo e auditado.

## Estrutura Do Projeto

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

## Licença

Licença MIT.

Criado e mantido por ByKurebo.
