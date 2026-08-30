import os
import shlex
from pathlib import Path

try:
    import readline
except ImportError:
    pass

from ContainerStuff.acess import restaurar_container
from ContainerStuff.wrapper import main_wrapper, verify, update_hash
from ContainerStuff.test import test_compatibility

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


def clear():
    """Clear the terminal using the current platform command."""
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    """Print the Harbor CLI banner."""
    print(
        f"""{MAGENTA}
======================================<[>>>          {BOLD}{WHITE}>>> HARBOR <<<{RESET}{MAGENTA}       <<<]>======================================{RESET}
Harbor, 2026, MIT License, {BOLD}v1.0.0{RESET}      {MAGENTA}|{RESET} Client-Center Mode                  {MAGENTA}|{RESET} Developed, deployed, and maintained by
Light-weight Open Source Docker CLI    {MAGENTA}|{RESET} This is the {BOLD}full suite{RESET}              {MAGENTA}|{RESET} >>>>>>>>>>>>>> {BOLD}{YELLOW}ByKurebo{RESET} <<<<<<<<<<<<<<
"""
    )


def main():
    """Run the interactive Harbor command line."""
    banner()

    while True:
        cmd = shlex.split(input(f"{BOLD}{CYAN}Harbor{RESET} > ").strip())
        print("")

        if len(cmd) == 0:
            continue

        elif cmd[0] == "exit":
            print(f"{BOLD}{RED}Exiting Harbor...{RESET}")
            break

        elif cmd[0] == "help":
            print(
                fr"""{BOLD}{CYAN}Available commands:{RESET}
{BOLD}{CYAN}  help{RESET}                   Show this help message
{BOLD}{CYAN}  exit{RESET}                   Exit Harbor
{BOLD}{CYAN}  clear{RESET}                  Clear the screen

{BOLD}{CYAN}  wrapper{RESET} <path>         Create a Harbor container
                             <path> is optional. Defaults to the current directory.

{BOLD}{CYAN}  acess{RESET}   <file> <out>   Restore an encrypted container
                             <file> is required: .bcb file path or name.
                             <out> is optional. Defaults to the current directory.

{BOLD}{CYAN}  test{RESET}    <path>         Check the compatibility of the project
                                            with the system                     

{BOLD}{CYAN}  verify{RESET}  <path>         Verify container hashes
{BOLD}{CYAN}  uphash{RESET}  <path>         Update container hashes
"""
            )

        elif cmd[0] == "clear":
            clear()
            banner()

        elif cmd[0] == "wrapper":
            if len(cmd) > 1:
                main_wrapper(Path(cmd[1]))
            else:
                main_wrapper()

        elif cmd[0] == "acess":
            if len(cmd) > 1:
                arquivo_bcb = Path(cmd[1])
                if len(cmd) > 2:
                    diretorio_saida = Path(cmd[2])
                else:
                    diretorio_saida = Path(".")
                senha = input(f"{BOLD}{CYAN}Enter password for the container: {RESET}")
                try:
                    restaurar_container(arquivo_bcb, senha, diretorio_saida)
                except ValueError as e:
                    print(e)
            else:
                print(
                    f"[{RED}ERROR{RESET}] Missing required argument: <file> "
                    "(path to the encrypted container). Type 'help' for usage."
                )

        elif cmd[0] == "verify":
            if len(cmd) > 1:
                verify(Path(cmd[1]))
            else:
                print(
                    f"[{RED}ERROR{RESET}] Missing required argument: <path> "
                    "(path to the container). Type 'help' for usage."
                )

        elif cmd[0] == "uphash":
            if len(cmd) > 1:
                ask = input(
"[?] Update container hashes? [y/N]: "
).strip().lower()

                if ask == "y":
                    update_hash(Path(cmd[1]))

                else:
                    print(f"[{RED}ERROR{RESET}] Action aborted")
            else:
                print(
                    f"[{RED}ERROR{RESET}] Missing required argument: <path> "
                    "(path to the container). Type 'help' for usage."
                )

        elif cmd[0] == "test":
            if len(cmd) > 1:
                test_compatibility(Path(cmd[1]))

            else:
                print(
                    f"[{RED}ERROR{RESET}] Missing required argument: <path> "
                    "(path to the container). Type 'help' for usage."
                )

        elif cmd[0] == "hi":
            print(fr"""{RESET}
{WHITE}{BOLD}2222222222222222222222222222222222222222222222222222222222222222222222      {WHITE}██{MAGENTA}╗{WHITE}  ██{MAGENTA}╗{WHITE} █████{MAGENTA}╗{WHITE} ██████{MAGENTA}╗{WHITE} ██████{MAGENTA}╗{WHITE}  ██████{MAGENTA}╗{WHITE} ██████{MAGENTA}╗{WHITE} 
{WHITE}{BOLD}2222222222222222222222222222222222222222222222222222222222222222222222      {WHITE}██{MAGENTA}║{WHITE}  ██{MAGENTA}║{WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}╗{WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}╗{WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}╗{WHITE}██{MAGENTA}╔═══{WHITE}██{MAGENTA}╗{WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}╗
{WHITE}{BOLD}222                                                                222      {WHITE}███████{MAGENTA}║{WHITE}███████{MAGENTA}║{WHITE}██████{MAGENTA}╔╝{WHITE}██████{MAGENTA}╔╝{WHITE}██{MAGENTA}║   {WHITE}██{MAGENTA}║{WHITE}██████{MAGENTA}╔╝
{WHITE}{BOLD}222                                                                222      {WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}║{WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}║{WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}╗{WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}╗{WHITE}██{MAGENTA}║   {WHITE}██{MAGENTA}║{WHITE}██{MAGENTA}╔══{WHITE}██{MAGENTA}╗
{WHITE}{BOLD}222    {MAGENTA}22222222222   2222222222222222222222222222222222222222222{WHITE}   222      {WHITE}██{MAGENTA}║  {WHITE}██{MAGENTA}║{WHITE}██{MAGENTA}║  {WHITE}██{MAGENTA}║{WHITE}██{MAGENTA}║  {WHITE}██{MAGENTA}║{WHITE}██████{MAGENTA}╔╝╚{WHITE}██████{MAGENTA}╔╝{WHITE}██{MAGENTA}║  {WHITE}██{MAGENTA}║
{WHITE}{BOLD}222    {MAGENTA}22222222222   2222222222222222222222222222222222222222222{WHITE}   222      {RESET}{MAGENTA}╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
{WHITE}{BOLD}222    {MAGENTA}22222222222   2222222222222222222222222222222222222222222{WHITE}   222
{WHITE}{BOLD}222    {MAGENTA}22222222222   2222222222222222222222222222222222222222222{WHITE}   222      {RESET} _     _       _     _     __        __   _       _     _   
{WHITE}{BOLD}222    {MAGENTA}22222222222   2222222222222222222222222222222222222222222{WHITE}   222      {RESET}| |   (_) __ _| |__ | |_   \ \      / /__(_) __ _| |__ | |_ 
{WHITE}{BOLD}222    {MAGENTA}22222222222   2222222222222222222222222222222222222222222{WHITE}   222      {RESET}| |   | |/ _` | '_ \| __|___\ \ /\ / / _ \ |/ _` | '_ \| __|
{WHITE}{BOLD}222    {MAGENTA}22222222222                                              {WHITE}   222      {RESET}| |___| | (_| | | | | ||_____\ V  V /  __/ | (_| | | | | |_ _
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}   2222222222222222222222222222222   222      {RESET}|_____|_|\__, |_| |_|\__|     \_/\_/ \___|_|\__, |_| |_|\__(_)   
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}   2222222222222222222222222222222   222      {RESET}         |___/                              |___/           
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}   2222222222222222222222222222222   222       {RESET}___                   ____                           
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}   2222222222222222222222222222222   222      {RESET}/ _ \ _ __   ___ _ __ / ___|  ___  _   _ _ __ ___ ___ 
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}   2222222222222222222222222222222   222      {RESET}| | | | '_ \ / _ \ '_ \\___ \ / _ \| | | | '__/ __/ _ \
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}                     2222222222222   222      {RESET}| |_| | |_) |  __/ | | |___) | (_) | |_| | | | (_|  __/_
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}   222222222222222   2222222222222   222      {RESET}\___/ | .__/ \___|_| |_|____/ \___/ \__,_|_|  \___\___(_)
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}   222222222222222   2222222222222   222            {RESET}|_|                                              
{WHITE}{BOLD}222    {MAGENTA}22222222222222222222222{WHITE}   222222222222222   2222222222222   222       {RESET}____             _             
{WHITE}{BOLD}222                              222222222222222                   222      {RESET}|  _ \  ___   ___| | _____ _ __ 
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222      {RESET}| | | |/ _ \ / __| |/ / _ \ '__|
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222      {RESET}| |_| | (_) | (__|   <  __/ |_   
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222      {RESET}|____/ \___/ \___|_|\_\___|_(_)   
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222      {RESET}All of it was made by {YELLOW}{BOLD}ByKurebo
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222      {RESET}{YELLOW}{BOLD}He{RESET} maintain this too
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222      {RESET}But his friend {YELLOW}{BOLD}GPT{RESET} refined and reformated the code :v
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222      {RESET}'This is more like a project administrator and compatibility suite
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222       {RESET}than a real Docker, but it works and i like it' ~ {YELLOW}{BOLD}ByKurebo{RESET}, 2026
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   2222222222222222222222222222   {MAGENTA}2222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222                                  {MAGENTA}2222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   {MAGENTA}2222222222   2222222222222222222222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   {MAGENTA}2222222222   2222222222222222222222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   {MAGENTA}2222222222   2222222222222222222222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   {MAGENTA}2222222222   2222222222222222222222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   {MAGENTA}2222222222   2222222222222222222222222222222{WHITE}   222
{WHITE}{BOLD}222    2222222222   {MAGENTA}2222222222   2222222222222222222222222222222{WHITE}   222
{WHITE}{BOLD}222                 {MAGENTA}2222222222{WHITE}                                     222
{WHITE}{BOLD}222    {MAGENTA}2222222222222222222222222222222222222222{WHITE}    2222222222222   222
{WHITE}{BOLD}222    {MAGENTA}2222222222222222222222222222222222222222{WHITE}    2222222222222   222
{WHITE}{BOLD}222    {MAGENTA}2222222222222222222222222222222222222222{WHITE}    2222222222222   222
{WHITE}{BOLD}222    {MAGENTA}2222222222222222222222222222222222222222{WHITE}    2222222222222   222
{WHITE}{BOLD}222    {MAGENTA}2222222222222222222222222222222222222222{WHITE}    2222222222222   222
{WHITE}{BOLD}222    {MAGENTA}2222222222222222222222222222222222222222{WHITE}    2222222222222   222
{WHITE}{BOLD}222    {MAGENTA}2222222222222222222222222222222222222222{WHITE}    2222222222222   222
{WHITE}{BOLD}222    {MAGENTA}2222222222222222222222222222222222222222{WHITE}    2222222222222   222
{WHITE}{BOLD}222                                                2222222222222   222
{WHITE}{BOLD}222    222222222222222222222  2222222222222222222222222222222222   222
{WHITE}{BOLD}222    222222222222222222222  2222222222222222222222222222222222   222
{WHITE}{BOLD}222    222222222222222222222  2222222222222222222222222222222222   222
{WHITE}{BOLD}222    222222222222222222222  2222222222222222222222222222222222   222
{WHITE}{BOLD}222    222222222222222222222  2222222222222222222222222222222222   222
{WHITE}{BOLD}222    222222222222222222222  2222222222222222222222222222222222   222
{WHITE}{BOLD}222    222222222222222222222  2222222222222222222222222222222222   222
{WHITE}{BOLD}222                                                                222
{WHITE}{BOLD}222                                                                222
{WHITE}{BOLD}2222222222222222222222222222222222222222222222222222222222222222222222
{WHITE}{BOLD}2222222222222222222222222222222222222222222222222222222222222222222222
""")

        else:
            print(
                f"[{RED}ERROR{RESET}] Unknown command: {cmd[0]}. "
                "Type 'help' for a list of commands."
            )


main()
