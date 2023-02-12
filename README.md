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
```

### Finally

```bash
git clone https://github.com/NathanVaughn/dotfiles.git
cd dtofiles
python ./install.py
```
