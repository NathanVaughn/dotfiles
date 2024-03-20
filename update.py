import shutil
import subprocess

from utils import IS_LINUX, IS_WINDOWS


def main():
    if pipx := shutil.which("pipx"):
        subprocess.run([pipx, "upgrade-all"])

    if npm := shutil.which("npm"):
        if IS_WINDOWS:
            npm = f"{npm}.cmd"
        subprocess.run([npm, "update", "-g"])

    if brew := shutil.which("brew"):
        subprocess.run([brew, "upgrade"])

    if IS_LINUX:
        if snap := shutil.which("snap"):
            subprocess.run(["sudo", snap, "refresh"])

        subprocess.run(["sudo", "apt", "update", "-y"])
        subprocess.run(["sudo", "apt", "upgrade", "-y"])
        subprocess.run(["sudo", "apt", "autoremove", "-y"])

    if IS_WINDOWS:
        # while sudo exists on Windows, it's not really an .exe
        # or anything, so python doesn't like it.
        subprocess.run(["winget", "upgrade", "--all"])


if __name__ == "__main__":
    main()
