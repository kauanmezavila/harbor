import shlex
import subprocess
import sys
from pathlib import Path

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

MAGENTA = "\033[95m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"

HARB_CMD_PREFIX = f"{BOLD}[{MAGENTA}HARB-IMG{WHITE}]{RESET}"


shell_status = True
capture_output = False
err_break = False
usr_log = True


def run_harb_command(command):
    global shell_status, capture_output, err_break, usr_log

    cmd = shlex.split(command)

    if not cmd:
        return

    if cmd[0] == "shell-mode":
        if len(cmd) < 2:
            shell_status = not shell_status
        elif cmd[1] == "on":
            shell_status = True
        elif cmd[1] == "off":
            shell_status = False
        else:
            print(f"[{RED}ERROR{RESET}] Use: shell-mode [on|off]")
            return

        if usr_log:
            print(f"{HARB_CMD_PREFIX} shell-mode: {shell_status}")

    elif cmd[0] == "output":
        if len(cmd) < 2:
            capture_output = not capture_output
        elif cmd[1] == "on":
            capture_output = True
        elif cmd[1] == "off":
            capture_output = False
        else:
            print(f"[{RED}ERROR{RESET}] Uso: output [on|off]")
            return

        if usr_log:
            print(f"{HARB_CMD_PREFIX} output: {capture_output}")

    elif cmd[0] == "err-break":
        if len(cmd) < 2:
            err_break = not err_break
        elif cmd[1] == "on":
            err_break = True
        elif cmd[1] == "off":
            err_break = False
        else:
            print(f"[{RED}ERROR{RESET}] Uso: err-break [on|off]")
            return

        if usr_log:
            print(f"{HARB_CMD_PREFIX} err-break: {err_break}")

    elif cmd[0] == "usr-log":
        if len(cmd) < 2:
            usr_log = not usr_log
        elif cmd[1] == "on":
            usr_log = True
        elif cmd[1] == "off":
            usr_log = False
        else:
            print(f"[{RED}ERROR{RESET}] Uso: err-break [on|off]")
            return

        print(f"{HARB_CMD_PREFIX} usr-log: {usr_log}")

    else:
        print(f"[{RED}ERROR{RESET}] Comando desconhecido: {cmd[0]}")


def run_command(command):
    if not command:
        return

    if shell_status:
        cmd = command
    else:
        try:
            cmd = shlex.split(command)
        except ValueError as e:
            print(f"[{RED}ERROR{RESET}] Invalid command syntax: {e}")

            if err_break:
                print(
                    f"[{YELLOW}LOG{RESET}] An error occurred, breaking process... [1]"
                )
                sys.exit(1)

            return

    if usr_log:
        print(
            f"{HARB_CMD_PREFIX} Running: {cmd[0] if not shell_status else command[:10] + '...'}\n"
        )

    try:
        result = subprocess.run(
            cmd,
            shell=shell_status,
            capture_output=capture_output,
            text=True,
            check=err_break,
        )

        if capture_output:
            if result.stdout:
                print(result.stdout, end="")

            if result.stderr:
                print(result.stderr, end="")

    except subprocess.CalledProcessError as e:
        print(
            f"[{RED}ERROR{RESET}] "
            f"Command '{command}' failed with return code {e.returncode}"
        )

        if capture_output:
            if e.stdout:
                print(e.stdout, end="")

            if e.stderr:
                print(e.stderr, end="")

        if err_break:
            print(f"[{YELLOW}LOG{RESET}] An error occurred, breaking process... [1]")
            sys.exit(1)

    except OSError as e:
        print(
            f"[{RED}ERROR{RESET}] "
            f"Command '{command}' failed "
            f"(can't determine return code, probably a Python traceback): {e}"
        )

        if err_break:
            print(f"[{YELLOW}LOG{RESET}] An error occurred, breaking process... [1]")
            sys.exit(1)


def run_line(path):
    install_file = Path(path).expanduser().resolve() / "Info" / ".harbinstall"

    with install_file.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith("hrb:>"):
                run_harb_command(line[5:].strip())

            elif line.startswith("#"):
                continue

            else:
                run_command(line)
