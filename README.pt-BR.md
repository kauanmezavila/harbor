<p align="center">
  <img src="imgs/HarborBanner.png" alt="Logo do Harbor">
</p>

<h1 align="center">Harbor</h1>

<p align="center">
  Uma CLI open source leve para empacotar projetos em containers Harbor portáteis com metadados, checagem de compatibilidade, hashes de integridade e exportação criptografada opcional.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Licença" src="https://img.shields.io/badge/Licen%C3%A7a-MIT-111111?style=for-the-badge">
  <img alt="Status" src="https://img.shields.io/badge/Status-v1.0.0-9b59b6?style=for-the-badge">
</p>

---

## O que é o Harbor?

Harbor transforma uma pasta de projeto em um pacote portátil no estilo container.

Ele escaneia a árvore do projeto, detecta stacks conhecidas, gera metadados, copia o código para uma área limpa `Code/`, guarda arquivos de raiz em `Info/`, cria hashes SHA-256 recursivos, compacta o resultado como `.harb` e também pode criar uma exportação `.bcb` criptografada por senha.

Harbor não é Docker. Ele é mais próximo de um empacotador, verificador e assistente de compatibilidade para projetos.

## Recursos

- `wrapper`: cria um container Harbor a partir de um diretório de projeto.
- `inflate`: extrai um container `.harb`.
- `restore`: descriptografa e extrai uma exportação `.bcb`.
- `verify`: valida a árvore recursiva de integridade `.hash.txt`.
- `uphash`: recalcula os hashes do container após mudanças intencionais.
- `compatibility`: checa o sistema operacional, a arquitetura e os runtimes atuais contra os metadados do container.
- `run`: roda um .harbinstall, um script de instalação
- Suporte a `.harbignore` com regras no estilo gitwildmatch.
- Detecção de stacks como Python, Node.js, Go, Rust, Java, Docker, React, Vue e mais.

## Instalação

```bash
git clone https://github.com/kauanmezavila/harbor.git
cd Harbor
```

Agora escolha o método mais adequado:

```bash
pip install .
python -m pip install .
pipx install .
```

(Nota: usamos `pyproject.toml` para habilitar o comando global.)

## Uso

```bash
harbor <comando> <args>
```

```text
Comandos:
  wrapper <path>                            Cria um container Harbor
  inflate <file.harb> [--out <directory>]   Extrai um container .harb
  restore <file.bcb> --password <password>  Restaura uma exportação .bcb criptografada
  verify <path>                             Verifica os hashes do container
  uphash <path>                             Recalcula os hashes do container
  compatibility <path>                      Checa a compatibilidade do container
  run <path>                                Roda o .harbinstall
```

Exemplos:

```bash
harbor wrapper MyApp
harbor inflate "MyApp-Any-Any-[HARBOR].harb" --out ./restored
harbor restore "MyApp-Any-Any-[HARBOR]_encrypted.bcb" --password "secret" --out ./restored
harbor verify "MyApp-Any-Any-[HARBOR]"
harbor compatibility "MyApp-Any-Any-[HARBOR]"
harbor run "MyApp-Any-Any-[HARBOR]"
```

Nota: por motivos de segurança, `run` só deve rodar o `.harbinstall` quando executado pela raiz do projeto.

## Saída do Container

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

Se a criptografia for ativada, o Harbor cria:

```text
MyApp-Any-Any-[HARBOR]_encrypted.bcb
```

A parte `Any-Any` muda quando você define arquiteturas ou sistemas operacionais específicos durante o empacotamento.

## Regras de Ignore

Adicione um arquivo `.harbignore` na raiz do projeto para excluir arquivos ou pastas do container, como um `.gitignore`.

Exemplo:

```gitignore
.git/
__pycache__/
node_modules/
*.log
```

## .harbinstall

Na versão 1.2.1, o Harbor passou a ter suporte ao `.harbinstall`: um arquivo que ajuda na instalação usando `subprocess`.

Para usar:

- Crie o arquivo de instalação como faria com um `.sh` ou `.bat`. Ele roda linha por linha.
- Adicione o índice `hrb:> ` e comandos HARB-IMG se quiser:

```bash
shell-mode  : roda comandos com shell ou lista de subprocess [começa como 'True']
output      : captura a saída [começa como 'False']
err-break   : determina se o HARB-IMG deve parar quando ocorrer erro [começa como 'False']
usr-log     : mostra os logs do HARB-IMG para o usuário [começa como 'True']
```

Nota: se você não escrever um `.harbinstall` na raiz, o Harbor colocará um vazio na pasta `Info` do container.

## Nota de Segurança

Exportações `.bcb` criptografadas usam AES-GCM através do pacote `cryptography`. Use para empacotamento e compartilhamento controlado, não como substituto de um processo de segurança completo e auditado para produção.

## Estrutura do Projeto

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

## Licença

Licença MIT.

Criado e mantido por ByKurebo.
