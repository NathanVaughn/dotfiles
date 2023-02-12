# dotfiles

## Install

I recommend installing `pyenv` first:

### Windows

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

### Linux

```bash
curl https://pyenv.run | bash
sudo apt install -y build-essential gdb lcov libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev libncurses5-dev libreadline-dev libsqlite3-dev libssl-dev lzma lzma-dev tk-dev uuid-dev zlib1g-dev
```

### Finally

```bash
git clone https://github.com/NathanVaughn/dotfiles.git
cd dtofiles
python ./install.py
```
