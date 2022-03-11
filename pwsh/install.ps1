param (
    [parameter(Mandatory=$true,
    ParameterSetName="appdata")]
    [switch]
    $appdata,

    [parameter(Mandatory=$true,
    ParameterSetName="progfiles")]
    [switch]
    $progfiles
 )

# install oh-my-posh
winget install JanDeDobbeleer.OhMyPosh

# install fonts
# magic folder
$fontdir = (New-Object -ComObject Shell.Application).Namespace(0x14)

$tmpdir =  Join-Path "$env:temp" "CascadiaCodeDownload"
New-Item $tmpdir -Type Directory -Force

# download url
$zipfile = Join-Path $tmpdir "CascadiaCode.zip"
Invoke-WebRequest -Uri "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/CascadiaCode.zip" -OutFile $zipfile

# extract zip
Expand-Archive $zipfile -DestinationPath $tmpdir -Force

# install fonts
Get-ChildItem -Path $tmpdir -Include '*.ttf','*.ttc','*.otf' -Recurse | ForEach {
    Write-Output $_.FullName
    $fontdir.CopyHere($_.FullName,0x10)
}

Remove-Item $tmpdir -Recurse -Force

# copy powershell profile
$docs = [Environment]::GetFolderPath("MyDocuments")
Copy-Item "Microsoft.PowerShell_profile.ps1" -Destination (Join-Path $docs "PowerShell")

# copy oh-my-posh theme
Copy-Item "../nathanv-me.omp.json" -Destination "$env:LOCALAPPDATA\Programs\oh-my-posh\themes\"

# copy windows terminal settings
if ($appdata) {
    $src = "wt_settings_appdata.json"
} elseif ($progfiles) {
    $src = "wt_settings_progfiles.json"
}
Copy-Item $src -Destination "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"

# copy pip config
if (-Not (Test-Path "$env:APPDATA\pip")) {
    New-Item "$env:APPDATA\pip" -ItemType Directory
}
if (-Not (Test-Path "$env:APPDATA\pip\pip.ini")) {
    Copy-Item pip.ini -Destination "$env:APPDATA\pip\pip.ini"
}
