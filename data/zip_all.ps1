# Get the directory where the script is located
$sourcePath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Get all files in the current folder, excluding .bat, .ps1, and .zip files
$files = Get-ChildItem -Path $sourcePath -File | Where-Object { $_.Extension -notin @('.bat', '.ps1', '.zip') }

# Loop through each file and create a zip file for it
foreach ($file in $files) {
    $zipFileName = $file.FullName + ".zip"
    Compress-Archive -Path $file.FullName -DestinationPath $zipFileName -Force
}

Write-Host "Zipping complete. Each file has been compressed into its own zip file."
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')