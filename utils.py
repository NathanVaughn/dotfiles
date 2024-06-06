import os
import platform
import shutil
import subprocess
import sys

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

def check_sudo() -> None:
    """
    Checks if the current process is running with administrator privileges, and
    if not, re-launch.
    """
    if IS_WINDOWS:
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            return

        # re run ourselves with admin
        print("Needing admin privileges, re-launching")

        try:
            sys.exit(
                subprocess.run(
                    ["runas", "/noprofile", "/user:Administrator", sys.executable]
                    + sys.argv
                ).returncode
            )
        except PermissionError:
            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(1)

    elif IS_LINUX:
        if os.geteuid() == 0:
            return

        # re run ourselves with sudo
        print("Needing sudo privileges, re-launching")

        try:
            sys.exit(
                subprocess.run(
                    ["sudo", "-E", sys.executable]
                    + sys.argv
                ).returncode
            )
        except PermissionError:
            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(1)