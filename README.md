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
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev
```

### Finally

```bash
git clone https://github.com/NathanVaughn/dotfiles.git
cd dtofiles
python ./install.py
```
