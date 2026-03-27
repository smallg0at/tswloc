# CHANGE THOSE VARIABLES TO YOUR OWN VALUES
$pakFile = "TS2Prototype-WindowsNoEditor-MedwayValleyLineStroodTonbridge.pak"
$outDir = "original/"
# find the absolute path of the original folder
$outDir = Join-Path (Get-Location) $outDir
Set-Location "D:\SteamLibrary\steamapps\common\Train Sim World 6\WindowsNoEditor\TS2Prototype\Content\DLC"

$locresPaths = repak list $pakFile |
Select-String "Localization" |
ForEach-Object { $_.ToString().Trim() } |
Where-Object { $_ -like "*.locres" }

if ($locresPaths.Count -gt 0) {
	Write-Host "Found $($locresPaths.Count) resource files, preparing to unpack..." -ForegroundColor Cyan
	$unpackArgs = @("unpack", $pakFile, "-o", $outDir)
	foreach ($path in $locresPaths) {
		$unpackArgs += "--include"
		$unpackArgs += $path
	}
	& repak @unpackArgs
}
else {
	Write-Host "No locres files found in $pakFile." -ForegroundColor Yellow
}