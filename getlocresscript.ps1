# CHANGE THOSE VARIABLES TO YOUR OWN VALUES
$pakFile = "TS2Prototype-WindowsNoEditor-LiberecStaraPaka.pak"
$outDir = "dist/"

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