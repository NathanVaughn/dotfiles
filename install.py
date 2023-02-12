import shutil
import os
import subprocess
import urllib.request
import zipfile
import tempfile
import sys

# colors
RED = "\033[0;31m"
LIGHTRED = "\033[1;31m"
GREEN = "\033[0;32m"
LIGHTGREEN = "\033[1;32m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color

IS_LINUX = os.name == "posix"
IS_WINDOWS = os.name == "nt"

APT_UPDATED = False

HOME_DIR = os.path.expanduser("~")
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

PKGS_DIR = os.path.join(THIS_DIR, "pkgs")
OMP_DIR = os.path.join(THIS_DIR, "oh-my-posh")
WINDOWS_DIR = os.path.join(THIS_DIR, "windows")
LINUX_DIR = os.path.join(THIS_DIR, "linux")

HAS_SUDO = False

if IS_LINUX:
    HAS_SUDO = os.geteuid() == 0

if IS_WINDOWS:
    APPDATA_DIR = os.environ["APPDATA"]
    LOCALAPPDATA_DIR = os.environ["LOCALAPPDATA"]

    import ctypes
    from ctypes.wintypes import MAX_PATH

    dll = ctypes.windll.shell32
    buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
    dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False)

    DOCUMENTS_DIR = buf.value


def w(program: str) -> str:
    ret = shutil.which(program)
    if ret is None:
        raise FileNotFoundError(f"Could not find {program}")
    return ret


def install_pip_settings() -> None:
    src = os.path.join(PKGS_DIR, "pip.ini")

    if IS_LINUX:
        target = os.path.join(HOME_DIR, ".config", "pip", "pip.conf")
    elif IS_WINDOWS:
        target = os.path.join(APPDATA_DIR, "pip", "pip.ini")
    else:
        raise EnvironmentError("Unsupported OS")

    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copy(src, target)

    print(f"Installed pip settings to {target}")


def install_npm_settings() -> None:
    src = os.path.join(PKGS_DIR, ".npmrc")
    target = os.path.join(HOME_DIR, ".npmrc")
    shutil.copy(src, target)

    print(f"Installed npm settings to {target}")


def install_windows_terminal_settings() -> None:
    src = os.path.join(WINDOWS_DIR, "wt_settings.json")
    target = os.path.join(
        LOCALAPPDATA_DIR,
        "Packages",
        "Microsoft.WindowsTerminal_8wekyb3d8bbwe",
        "LocalState",
        "settings.json",
    )
    shutil.copy(src, target)

    print(f"Installed Windows Terminal settings to {target}")


def install_powershell_profile() -> None:
    src = os.path.join(WINDOWS_DIR, "Microsoft.PowerShell_profile.ps1")
    target = os.path.join(
        DOCUMENTS_DIR, "PowerShell", "Microsoft.PowerShell_profile.ps1"
    )
    shutil.copy(src, target)

    print(f"Installed PowerShell profile to {target}")


def set_git_config_key_value(key: str, value: str) -> None:
    print(f"Configuring git {key}")

    subprocess.check_call([w("git"), "config", "--global", key, value])


def install_apt_package(package: str) -> None:
    global APT_UPDATED

    if not APT_UPDATED:
        subprocess.check_call([w("apt-get"), "update", "-y"])
        APT_UPDATED = True

    subprocess.check_call([w("apt-get"), "install", "-y", package])


def update_git() -> None:
    subprocess.check_call([w("add-apt-repository"), "ppa:git-core/ppa", "-y"])
    install_apt_package("git")


def rewrite_apt_sources() -> None:
    subprocess.check_call(
        [sys.executable, os.path.join(LINUX_DIR, "rewrite_apt_sources.py")]
    )


def set_git_config(email: bool, gpg: bool) -> None:
    set_git_config_key_value("user.name", "Nathan Vaughn")

    set_git_config_key_value("color.status.added", "green bold")
    set_git_config_key_value("color.status.changed", "red bold strike")
    set_git_config_key_value("color.status.untracked", "cyan")
    set_git_config_key_value("color.status.branch", "yellow black bold ul")

    set_git_config_key_value("init.defaultBranch", "main")
    set_git_config_key_value("help.autoCorrect", "prompt")
    set_git_config_key_value("core.fsmonitor", "true")
    set_git_config_key_value("credential.helper", "store")

    if email:
        set_git_config_key_value("user.email", "nvaughn51@gmail.com")

    if gpg:
        set_git_config_key_value(
            "user.signingkey", "958AB43C3CBC4E7EBBC1979769893C308784B59B"
        )
        set_git_config_key_value("commit.gpgsign", "true")

        if IS_WINDOWS:
            set_git_config_key_value(
                "gpg.program", "C:\\Program Files\\Git\\usr\\bin\\gpg.exe"
            )


def install_apt_packages() -> None:
    packages = [
        "software-properties-common",
        "python-is-python3",
        "bat",
        "unzip",
        "fontconfig",
        "nala",
    ]
    for package in packages:
        install_apt_package(package)


def install_bash_settings() -> None:
    for file in os.listdir(LINUX_DIR):
        if not file.startswith("."):
            continue

        src = os.path.join(LINUX_DIR, file)
        target = os.path.join(HOME_DIR, file)

        os.remove(target)

        print(f"Linking {src} to {target}")
        os.symlink(src, target)


def install_oh_my_posh() -> None:
    print("Installing oh-my-posh")

    if IS_WINDOWS:
        subprocess.run([w("winget"), "install", "JanDeDobbeleer.OhMyPosh"])

        posh_themes = os.path.join(LOCALAPPDATA_DIR, "Programs", "oh-my-posh", "themes")
        os.makedirs(posh_themes, exist_ok=True)

        shutil.copy(os.path.join(OMP_DIR, "nathanv-me.omp.json"), posh_themes)

    elif IS_LINUX:
        local_bin = os.path.join(HOME_DIR, ".local", "bin")
        os.makedirs(local_bin, exist_ok=True)

        url = "https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/posh-linux-amd64"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, os.path.join(local_bin, "oh-my-posh"))
        subprocess.check_call(["chmod", "+x", os.path.join(local_bin, "oh-my-posh")])

        print("Installing oh-my-posh themes")
        posh_themes = os.path.join(HOME_DIR, ".poshthemes")
        os.makedirs(posh_themes, exist_ok=True)

        url = "https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/themes.zip"
        print(f"Downloading {url}")
        themes_zip, _ = urllib.request.urlretrieve(url)
        with zipfile.ZipFile(themes_zip, "r") as zip_ref:
            # delete target contents first
            for member in zip_ref.namelist():
                if os.path.isfile(os.path.join(posh_themes, member)):
                    os.remove(os.path.join(posh_themes, member))

            zip_ref.extractall(posh_themes)

        os.remove(themes_zip)

        shutil.copy(os.path.join(OMP_DIR, "nathanv-me.omp.json"), posh_themes)
        subprocess.check_call(["chmod", "-R", "u+rw", posh_themes])


def install_fonts() -> None:
    if IS_WINDOWS:
        target = tempfile.mkdtemp()
        # target = os.path.join(LOCALAPPDATA_DIR, "Microsoft", "Windows", "Fonts")
    elif IS_LINUX:
        target = os.path.join(HOME_DIR, ".local", "share", "fonts")
    else:
        raise EnvironmentError("Unsupported OS")

    url = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/CascadiaCode.zip"

    print(f"Downloading {url}")
    fonts_zip, _ = urllib.request.urlretrieve(url)

    print(f"Extracting {fonts_zip}")
    with zipfile.ZipFile(fonts_zip, "r") as zip_ref:
        zip_ref.extractall(target)

    os.remove(fonts_zip)

    if IS_LINUX:
        subprocess.check_call(["fc-cache", "-fv"])
    elif IS_WINDOWS:
        subprocess.check_call(
            [w("powershell"), os.path.join(WINDOWS_DIR, "install_fonts.ps1"), target]
        )
        shutil.rmtree(target)


def get_response(prompt: str, new_line: bool = True) -> bool:
    full_prompt = f"{BOLD}Would you like to {prompt}? {NC}"
    if new_line:
        full_prompt = "\n" + full_prompt

    val = input(full_prompt).strip().lower()
    return val.startswith("y")


def main() -> None:
    if IS_LINUX and HAS_SUDO:
        rewrite_apt_sources_bool = get_response("rewrite apt sources")

        if rewrite_apt_sources_bool:
            rewrite_apt_sources()

        if get_response("install apt packages"):
            install_apt_packages()

        if get_response("update git"):
            update_git()
            if rewrite_apt_sources_bool:
                rewrite_apt_sources()

    if IS_LINUX and get_response("install Bash settings"):
        install_bash_settings()

    if get_response("configure git"):
        email = get_response("set git's email to your personal address", new_line=False)
        gpg = get_response("configure git to use your GPG key", new_line=False)
        set_git_config(email=email, gpg=gpg)

    if get_response("install fonts"):
        install_fonts()

    if get_response("install oh-my-posh"):
        install_oh_my_posh()

    if IS_WINDOWS:
        if get_response("install your PowerShell profile"):
            install_powershell_profile()

        if get_response("install Windows Terminal settings"):
            install_windows_terminal_settings()

    if get_response("install pip settings"):
        install_pip_settings()

    if get_response("install npm settings"):
        install_npm_settings()

    if IS_WINDOWS:
        print(
            f"{GREEN}Done.{NC} Run {BOLD}. $PROFILE{NC} to refresh your PowerShell profile."
        )
    elif IS_LINUX:
        print(
            f"{GREEN}Done.{NC} Run {BOLD}source ~/.bash_profile{NC} to refresh your Bash profile."
        )


if __name__ == "__main__":
    main()
