# Get the directory where the script is located
$sourcePath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Get all zip files in the current folder
$zipFiles = Get-ChildItem -Path $sourcePath -Filter *.zip

# Loop through each zip file and extract its contents
foreach ($zipFile in $zipFiles) {
    $destinationPath = Join-Path -Path $sourcePath -ChildPath $zipFile.BaseName
    
    # Create the destination folder if it doesn't exist
    if (!(Test-Path -Path $destinationPath)) {
        New-Item -ItemType Directory -Path $destinationPath | Out-Null
    }
    
    # Unzip the file
    Expand-Archive -Path $zipFile.FullName -DestinationPath $destinationPath -Force
    
    Write-Host "Unzipped: $($zipFile.Name) to $destinationPath"
}

Write-Host "Unzipping complete. All zip files have been extracted."
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')