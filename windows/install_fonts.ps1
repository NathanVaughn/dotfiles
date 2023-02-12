param ($src)

$fontdir = (New-Object -ComObject Shell.Application).Namespace(0x14)
Get-ChildItem -Path $src -Include '*.ttf','*.ttc','*.otf' -Recurse | ForEach {
    Write-Output $_.FullName
    $fontdir.CopyHere($_.FullName,0x10)
}