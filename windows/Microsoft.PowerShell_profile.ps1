del alias:clc -Force

New-Alias activate ./.venv/Scripts/activate
New-Alias ifconfig ipconfig
New-Alias clc clear
New-Alias ll ls

function uuid { [guid]::NewGuid().ToString() }
function guid { [guid]::NewGuid().ToString() }
function venv { uv run python -m venv .venv }
function rm-rf { Remove-Item -Recurse -Force $args }
function sudo { Start-Process powershell -Verb runAs $args }

# disable virtual environment prompt as theme already shows it
$env:VIRTUAL_ENV_DISABLE_PROMPT=1

# disable Az.Accounts powershell module to speed things up
$env:AZ_ENABLED=$false

oh-my-posh init pwsh --config "${env:ProgramFiles(x86)}\oh-my-posh\themes\nathanv-me.omp.json" | Invoke-Expression