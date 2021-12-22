New-Alias activate ./.venv/Scripts/activate
New-Alias ifconfig ipconfig
function venv { python -m venv .venv }

# disable virtual environment prompt as theme already shows it
$env:VIRTUAL_ENV_DISABLE_PROMPT=1

# disable Az.Accounts powershell module to speed things up
$env:AZ_ENABLED=$false

~\AppData\Local\Programs\oh-my-posh\bin\oh-my-posh.exe --init --shell pwsh --config ~\AppData\Local\Programs\oh-my-posh\themes\nathanv-me.omp.json | Invoke-Expression