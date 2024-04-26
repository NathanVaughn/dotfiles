import functools
import getpass
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from typing import Any, Callable, List, Union

from utils import IS_LINUX, IS_WINDOWS, IS_WSL, run, which

# our tracking
APT_UPDATED = False

# directories
HOME_DIR = os.path.expanduser("~")
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

PKGS_DIR = os.path.join(THIS_DIR, "pkgs")
OMP_DIR = os.path.join(THIS_DIR, "oh-my-posh")
WINDOWS_DIR = os.path.join(THIS_DIR, "windows")
LINUX_DIR = os.path.join(THIS_DIR, "linux")


# our constants
BREW_PATH = "/home/linuxbrew/.linuxbrew/bin/brew"
# colors
RED = "\033[0;31m"
LIGHTRED = "\033[1;31m"
GREEN = "\033[0;32m"
LIGHTGREEN = "\033[1;32m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color


if IS_LINUX and os.geteuid() == 0:
    print(f"{RED}Rerun {BOLD}without{NC}{RED} sudo.{NC}")
    sys.exit(1)

if IS_WINDOWS:
    APPDATA_DIR = os.environ["APPDATA"]
    LOCALAPPDATA_DIR = os.environ["LOCALAPPDATA"]

    import ctypes
    from ctypes.wintypes import MAX_PATH

    dll = ctypes.windll.shell32
    buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
    dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False)

    DOCUMENTS_DIR = buf.value


def warn(msg: str) -> None:
    """
    Print a warning.
    """
    print(f"{RED}{msg}{NC}")


def info(msg: str) -> None:
    """
    Print a warning.
    """
    print(f"{BOLD}{msg}{NC}")


def has_winget() -> bool:
    """
    Checks if winget is installed.
    """
    return bool(shutil.which("winget"))


def has_homebrew() -> bool:
    """
    Checks if homebrew is installed
    """
    which = bool(shutil.which("brew"))
    return True if which else os.path.isfile(BREW_PATH)


def download_file(url: str) -> str:
    """
    Downloads a file and then returns the temp file path.
    """
    print(f"Downloading {url}")
    file, _ = urllib.request.urlretrieve(url)
    return file


def sudo(command: List[str]) -> List[str]:
    """
    Wraps a list of commands with sudo
    """
    return ["sudo"] + command


def set_git_config_key_value(key: str, value: str) -> None:
    """
    Sets a git config value globally
    """
    print(f"Configuring git {key}")
    run(["git", "config", "--global", key, value])


def apt_install_packages(packages: Union[str, List[str]]) -> None:
    """
    Install one or more apt packages
    """
    global APT_UPDATED

    if not APT_UPDATED:
        run(sudo(["apt-get", "update", "-y"]))
        APT_UPDATED = True

    cmd = sudo(["apt-get", "install", "-y"])

    if isinstance(packages, list):
        cmd += packages
    else:
        cmd += [packages]

    run(cmd)


def bash_run_script_from_url(url: str) -> None:
    """
    Run an bash script from a URL
    """
    installer = download_file(url)
    run(["bash", installer])
    os.remove(installer)


def powershell_run_script_from_url(url: str) -> None:
    """
    Run an powershell script from a URL
    """
    installer = download_file(url)
    # powershell needs the file to end in .ps1
    installer_ps1 = f"{installer}.ps1"
    os.rename(installer, installer_ps1)

    run(["powershell", installer_ps1])
    os.remove(installer_ps1)


def install_deb_from_url(url: str) -> None:
    """
    Install a .deb file from a URL
    """
    deb_file = download_file(url)
    run(sudo(["dpkg", "-i", deb_file]))
    os.remove(deb_file)


def homebrew_install(package: str) -> None:
    """
    Install a package with brew
    """
    if not has_homebrew():
        warn(f"Homebrew is not installed, skipping install of {package}")
        return

    run([BREW_PATH, "install", package])


def winget_install(package: str) -> None:
    """
    Install a package with Winget
    """
    if not has_winget():
        warn(f"Winget is not installed, skipping install of {package}")
        return

    # if a package is already installed, error code will be non zero
    run(["winget", "install", package], check=False)


def snap_install(package: str, classic: bool = False) -> None:
    """
    Install a snap package
    """
    cmd = sudo(["snap", "install", package])
    if classic:
        cmd += ["--classic"]
    run(cmd)


def get_response(prompt: str) -> bool:
    """
    Prompt user with something and get a boolean response
    """
    full_prompt = f"{BOLD}Would you like to {prompt}? {NC}"
    val = input(full_prompt).strip().lower()
    return val.startswith("y")


def add_line_to_file(filename: str, newline: str) -> None:
    """
    Add a new line to a file. If an existing line is found with the same
    starting string, it will be replaced.
    """
    newline += "\n"

    # read file
    with open(filename, "r") as fp:
        lines = fp.readlines()

    key = newline.split(" ", maxsplit=1)[0]

    # replace matching line
    found = False

    for i, line in enumerate(lines):
        if line.startswith(key):
            if line == newline:
                return

            lines[i] = newline
            found = True
            break

    if not found:
        lines.append(newline)

    # write new contents
    with open(filename, "w") as fp:
        fp.writelines(lines)


# decorators
# =======================================
def response(prompt: str) -> Callable:
    """
    Decorator to require a response to run the function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if get_response(prompt):
                func(*args, **kwargs)
                return True

        return wrapper

    return decorator


def require_windows(func: Callable) -> Callable:
    """
    Decorator to only run on Windows
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if IS_WINDOWS:
            return func(*args, **kwargs)

    return wrapper


def require_linux(func: Callable) -> Callable:
    """
    Decorator to only run on Linux
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if IS_LINUX:
            return func(*args, **kwargs)

    return wrapper


# utilities
# =======================================
@require_linux
@response("use the git-core PPA and update Git")
def install_util_git_update() -> None:
    apt_install_packages("software-properties-common")
    run(sudo(["add-apt-repository", "ppa:git-core/ppa", "-y"]))
    apt_install_packages("git")


# runtimes
# =======================================


@require_windows
@response("install Powershell Core and Windows Terminal")
def install_runtime_powershell_core() -> None:
    winget_install("9MZ1SNWT0N5D")  # powershell core
    winget_install("9N0DX20HK701")  # windows terminal


@response("install NodeJS and NPM")
def install_runtime_nodejs() -> None:
    if IS_LINUX:
        snap_install("node", classic=True)
    elif IS_WINDOWS:
        winget_install("OpenJS.NodeJS.LTS")


@require_linux
@response("install Homebrew")
def install_runtime_homebrew() -> None:
    bash_run_script_from_url(
        "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
    )

    apt_install_packages("build-essential")
    run([BREW_PATH, "install", "gcc"])


@response("install/update pyenv")
def install_runtime_pyenv() -> None:
    if IS_WINDOWS:
        # https://github.com/pyenv-win/pyenv-win/blob/master/docs/installation.md#powershell
        powershell_run_script_from_url(
            "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1"
        )
    elif IS_LINUX:
        if shutil.which("pyenv"):
            run(["pyenv", "update"])
        else:
            packages = [
                "pkg-config",
                "build-essential",
                "gdb",
                "lcov",
                "libbz2-dev",
                "libffi-dev",
                "libgdbm-dev",
                "libgdbm-compat-dev",
                "liblzma-dev",
                "libncurses5-dev",
                "libreadline6-dev",
                "libsqlite3-dev",
                "libssl-dev",
                "lzma",
                "lzma-dev",
                "tk-dev",
                "uuid-dev",
                "zlib1g-dev",
            ]
            apt_install_packages(packages)
            bash_run_script_from_url("https://pyenv.run")


# apps
# =======================================
@response("install Docker")
def install_app_docker() -> None:
    if IS_LINUX:
        bash_run_script_from_url("https://get.docker.com")
    elif IS_WINDOWS:
        winget_install("Docker.DockerDesktop")


@response("install Google Chrome")
def install_app_chrome() -> None:
    if IS_LINUX:
        install_deb_from_url(
            "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
        )
    elif IS_WINDOWS:
        winget_install("Google.Chrome")


@response("install Steam")
def install_app_steam() -> None:
    if IS_LINUX:
        install_deb_from_url(
            "https://media.steampowered.com/client/installer/steam.deb"
        )
    elif IS_WINDOWS:
        winget_install("Valve.Steam")


@response("install Spotify")
def install_app_spotify() -> None:
    if IS_LINUX:
        snap_install("spotify")
    elif IS_WINDOWS:
        # install from store
        winget_install("9NCBCSZSJRSB")


@response("install VS Code")
def install_app_vscode() -> None:
    if IS_LINUX:
        snap_install("code")
    elif IS_WINDOWS:
        winget_install("XP9KHM4BK9FZ7Q")


@response("install Libreoffice")
def install_app_libreoffice() -> None:
    if IS_LINUX:
        apt_install_packages("libreoffice")
    elif IS_WINDOWS:
        winget_install("TheDocumentFoundation.LibreOffice")


@response("install Discord")
def install_app_discord() -> None:
    if IS_LINUX:
        # 403 forbidden
        # _deb_installer("https://discord.com/api/download?platform=linux&format=deb")
        snap_install("discord")
    elif IS_WINDOWS:
        # install from store
        winget_install("XPDC2RH70K22MN")


# settings
# =======================================
@require_linux
@response("change the default apt sources")
def install_settings_apt_registry() -> None:
    os.environ["NEXUS_USERNAME"] = input("Enter your Nexus username: ")
    os.environ["NEXUS_PASSWORD"] = getpass.getpass(
        "Enter your Nexus password: ",
    )
    run(sudo([sys.executable, os.path.join(LINUX_DIR, "rewrite_apt_sources.py")]))


@require_linux
@response("install favorite apt packages")
def install_settings_favorite_apt_packages() -> None:
    packages = [
        "python-is-python3",
        "bat",
        "neofetch",
        "net-tools",
        "iputils-ping",
    ]
    apt_install_packages(packages)


@require_windows
@response("install favorite Winget packages")
def install_settings_favorite_winget_packages() -> None:
    packages = [
        "9NBLGGH516XP",  # ear trumpet
        "9P7KNL5RWT25",  # sysinternals
    ]
    for package in packages:
        winget_install(package)


@response("change the default Pip registry")
def install_settings_pip_registry() -> None:
    src = os.path.join(PKGS_DIR, "pip.ini")

    if IS_LINUX:
        target = os.path.join(HOME_DIR, ".config", "pip", "pip.conf")
    elif IS_WINDOWS:
        target = os.path.join(APPDATA_DIR, "pip", "pip.ini")
    else:
        raise EnvironmentError("Unsupported OS")

    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copy(src, target)

    print(f"Installed pip config to {target}")


@response("change the default NPM registry")
def install_settings_npm_registry() -> None:
    src = os.path.join(PKGS_DIR, ".npmrc")
    target = os.path.join(HOME_DIR, ".npmrc")
    shutil.copy(src, target)

    print(f"Installed npm settings to {target}")


@require_windows
@response("install the Windows Terminal settings")
def install_settings_windows_terminal() -> None:
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


@require_windows
@response("install the Powershell profile")
def install_settings_powershell_profile() -> None:
    src = os.path.join(WINDOWS_DIR, "Microsoft.PowerShell_profile.ps1")
    target = os.path.join(
        DOCUMENTS_DIR, "PowerShell", "Microsoft.PowerShell_profile.ps1"
    )
    shutil.copy(src, target)

    print(f"Installed PowerShell profile to {target}")


@require_linux
@response("install the Bash profile")
def install_settings_bash_profile() -> None:
    for file in os.listdir(LINUX_DIR):
        if not file.startswith("."):
            continue

        src = os.path.join(LINUX_DIR, file)
        target = os.path.join(HOME_DIR, file)

        if os.path.isfile(target) or os.path.islink(target):
            os.remove(target)

        print(f"Linking {src} to {target}")
        os.symlink(src, target)


@response("install fonts")
def install_settings_fonts() -> None:
    if IS_WINDOWS:
        target = tempfile.mkdtemp()
        # target = os.path.join(LOCALAPPDATA_DIR, "Microsoft", "Windows", "Fonts")
    elif IS_LINUX:
        target = os.path.join(HOME_DIR, ".local", "share", "fonts")
    else:
        raise EnvironmentError("Unsupported OS")

    fonts_zip = download_file(
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/CascadiaCode.zip"
    )

    print(f"Extracting {fonts_zip}")
    with zipfile.ZipFile(fonts_zip, "r") as zip_ref:
        zip_ref.extractall(target)

    os.remove(fonts_zip)

    if IS_LINUX:
        apt_install_packages("fontconfig")
        run(sudo(["fc-cache", "-fv"]))
    elif IS_WINDOWS:
        run(["powershell", os.path.join(WINDOWS_DIR, "install_fonts.ps1"), target])
        shutil.rmtree(target)


@response("install/update oh-my-posh")
def install_settings_oh_my_posh() -> None:
    if IS_WINDOWS:
        winget_install("JanDeDobbeleer.OhMyPosh")
        posh_themes = os.path.join(LOCALAPPDATA_DIR, "Programs", "oh-my-posh", "themes")

    elif IS_LINUX:
        homebrew_install("jandedobbeleer/oh-my-posh/oh-my-posh")
        posh_themes = os.path.join(HOME_DIR, ".poshthemes")
    else:
        raise ValueError

    os.makedirs(posh_themes, exist_ok=True)
    shutil.copy(os.path.join(OMP_DIR, "nathanv-me.omp.json"), posh_themes)


@response("install Git settings")
def install_settings_git_config() -> None:
    email = get_response("set the Git email to your personal address")
    gpg = get_response("configure Git to use your GPG key")

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

        elif IS_WSL:
            apt_install_packages(["gpg", "gnupg2", "socat"])

            set_git_config_key_value(
                "gpg.program", "/mnt/c/Program Files/Git/usr/bin/gpg.exe"
            )
            add_line_to_file(
                os.path.join(HOME_DIR, ".gnupg", "gpg-agent.conf"),
                "pinentry-program /mnt/c/Program Files/Git/usr/bin/pinentry.exe",
            )

            run(["gpg-connect-agent", "reloadagent", "/bye"])

        elif IS_LINUX:
            apt_install_packages(["gpg", "gnupg2"])

            set_git_config_key_value("gpg.program", which("gpg"))


@require_linux
@response("install Gnome-tweaks")
def install_settings_gnome_tweaks() -> None:
    apt_install_packages(["gnome-tweaks", "gnome-browser-connector"])
    info("Remember to open https://extensions.gnome.org/ afterwards")


@response("install Bing daily wallpaper")
def install_settings_bing_wallpaper() -> None:
    if IS_WINDOWS:
        winget_install("9NBLGGH1ZBKW")
    elif IS_LINUX:
        snap_install("bing-wall")


def main() -> None:
    # utils
    install_util_git_update()

    # runtimes
    # install_runtime_nodejs()
    install_runtime_homebrew()
    install_runtime_pyenv()

    # apps
    install_app_docker()
    install_app_chrome()
    install_app_steam()
    install_app_spotify()
    install_app_vscode()
    install_app_libreoffice()
    install_app_discord()

    # settings
    install_settings_apt_registry()
    install_settings_favorite_apt_packages()
    install_settings_favorite_winget_packages()
    install_settings_pip_registry()
    install_settings_npm_registry()
    powershell_profile_installed = install_settings_powershell_profile()
    install_settings_windows_terminal()
    bash_profile_installed = install_settings_bash_profile()
    install_settings_fonts()
    install_settings_oh_my_posh()
    install_settings_git_config()
    install_settings_gnome_tweaks()
    install_settings_bing_wallpaper()

    if powershell_profile_installed:
        print(f"Run {BOLD}. $PROFILE{NC} to refresh your PowerShell profile.")
    if bash_profile_installed:
        print(
            f"Run {BOLD}source {HOME_DIR}/.bash_profile{NC} to refresh your Bash profile."
        )


if __name__ == "__main__":
    main()
