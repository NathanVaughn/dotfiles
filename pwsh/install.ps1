winget install JanDeDobbeleer.OhMyPosh

# magic folder
$fontdir = (New-Object -ComObject Shell.Application).Namespace(0x14)

$tmpdir =  Join-Path "$env:temp" "CascadiaCodeDownload"
New-Item $tmpdir -Type Directory -Force

# download url
$zipfile = Join-Path $tmpdir "CascadiaCode.zip"
Invoke-WebRequest -Uri "https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/CascadiaCode.zip" -OutFile $zipfile

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