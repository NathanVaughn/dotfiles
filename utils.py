import os
import platform
import shutil
import subprocess

IS_LINUX = os.name == "posix"
IS_WINDOWS = os.name == "nt"
IS_WSL = "microsoft-standard" in platform.uname().release


def which(program: str) -> str:
    """
    shutil.which, but with an assert to make sure the program was found.
    """
    ret = shutil.which(program)
    if ret is None:
        raise FileNotFoundError(f"Could not find {program}")
    return ret


def run(command: list[str], check: bool = True) -> None:
    """
    Runs a command
    """
    cmd = [which(command[0])] + command[1:]
    print(f"\t{' '.join(cmd)}")

    if check:
        subprocess.check_call(cmd)
    else:
        subprocess.run(cmd)
