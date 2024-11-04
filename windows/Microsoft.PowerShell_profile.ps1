del alias:clc -Force

New-Alias activate ./.venv/Scripts/activate
New-Alias ifconfig ipconfig
New-Alias clc clear
New-Alias ll ls

function guid { [guid]::NewGuid().ToString() }
function venv { python -m venv .venv }
function rm-rf { Remove-Item -Recurse -Force $args }
function sudo { Start-Process powershell -Verb runAs $args }

# disable virtual environment prompt as theme already shows it
$env:VIRTUAL_ENV_DISABLE_PROMPT=1

# disable Az.Accounts powershell module to speed things up
$env:AZ_ENABLED=$false

~\AppData\Local\Programs\oh-my-posh\bin\oh-my-posh.exe init pwsh --config $HOME\AppData\Local\Programs\oh-my-posh\themes\nathanv-me.omp.json | Invoke-Expression