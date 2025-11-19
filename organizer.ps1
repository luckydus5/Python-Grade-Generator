# organizer.ps1
# Archives CSV files with timestamp and logs to organizer.log (PowerShell version)

$ARCHIVE_DIR = "archive"
$LOG_FILE = "organizer.log"

# Create archive dir if it doesn't exist
if (-Not (Test-Path $ARCHIVE_DIR)) {
    New-Item -ItemType Directory -Path $ARCHIVE_DIR | Out-Null
}

# Get all CSV files in current directory
$csvFiles = Get-ChildItem -Path . -Filter "*.csv" -File

if ($csvFiles.Count -eq 0) {
    Write-Host "No .csv files found in $(Get-Location). Nothing to do."
    exit 0
}

foreach ($file in $csvFiles) {
    # Generate timestamp (format: YYYYMMDD-HHMMSS)
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $baseName = $file.BaseName
    $newName = "${baseName}-${timestamp}.csv"
    
    # If file with same name exists (unlikely), append random suffix
    $destPath = Join-Path $ARCHIVE_DIR $newName
    if (Test-Path $destPath) {
        $rand = Get-Random -Minimum 0 -Maximum 9999
        $newName = "${baseName}-${timestamp}-$($rand.ToString('0000')).csv"
        $destPath = Join-Path $ARCHIVE_DIR $newName
    }
    
    # Log the action with timestamp and file content
    $logEntry = @"
=== Archive Log Entry ===
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Original File: $($file.Name)
New Location: $ARCHIVE_DIR\$newName
--- File Content ---
$(Get-Content $file.FullName -Raw)
--- End of Content ---

"@
    
    Add-Content -Path $LOG_FILE -Value $logEntry
    
    # Move file to archive with new name
    Move-Item -Path $file.FullName -Destination $destPath
    Write-Host "Archived: $($file.Name) -> $ARCHIVE_DIR\$newName"
}

Write-Host "Done. Archived $($csvFiles.Count) file(s). Check $LOG_FILE for details."
