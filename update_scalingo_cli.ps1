# Script to update Scalingo CLI to the latest version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Updating Scalingo CLI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current version
Write-Host "Current version:" -ForegroundColor Yellow
$currentVersion = scalingo --version 2>&1 | Select-String -Pattern "version (\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
Write-Host "  $currentVersion" -ForegroundColor Gray
Write-Host ""

# Find current installation path
$scalingoPath = (Get-Command scalingo).Source
$scalingoDir = Split-Path -Parent $scalingoPath
Write-Host "Current installation:" -ForegroundColor Yellow
Write-Host "  $scalingoPath" -ForegroundColor Gray
Write-Host ""

# Download latest version
Write-Host "Downloading latest version..." -ForegroundColor Yellow
# Try multiple download URLs
$downloadUrls = @(
    "https://github.com/Scalingo/cli/releases/download/v1.41.0/scalingo_windows_amd64.exe",
    "https://github.com/Scalingo/cli/releases/latest/download/scalingo_windows_amd64.exe",
    "https://cli-dl.scalingo.com/windows/scalingo_windows_amd64.exe"
)
$tempFile = "$env:TEMP\scalingo_latest.exe"
$downloadSuccess = $false

try {
    # Try with TLS 1.2
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $ProgressPreference = 'SilentlyContinue'
    
    foreach ($downloadUrl in $downloadUrls) {
        try {
            Write-Host "  Trying: $downloadUrl" -ForegroundColor Gray
            Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -ErrorAction Stop
            $downloadSuccess = $true
            break
        } catch {
            Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor DarkYellow
            continue
        }
    }
    
    if (-not $downloadSuccess) {
        throw "All download URLs failed"
    }
    
    Write-Host "✅ Download completed" -ForegroundColor Green
    Write-Host ""
    
    # Backup current version
    Write-Host "Backing up current version..." -ForegroundColor Yellow
    $backupPath = "$scalingoDir\scalingo_backup.exe"
    Copy-Item -Path $scalingoPath -Destination $backupPath -Force
    Write-Host "✅ Backup created: $backupPath" -ForegroundColor Green
    Write-Host ""
    
    # Replace with new version
    Write-Host "Installing new version..." -ForegroundColor Yellow
    Copy-Item -Path $tempFile -Destination $scalingoPath -Force
    Write-Host "✅ Installation completed" -ForegroundColor Green
    Write-Host ""
    
    # Verify new version
    Write-Host "Verifying installation..." -ForegroundColor Yellow
    $newVersion = scalingo --version 2>&1 | Select-String -Pattern "version (\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
    Write-Host "New version: $newVersion" -ForegroundColor Green
    Write-Host ""
    
    if ($newVersion -ne $currentVersion) {
        Write-Host "✅ Scalingo CLI successfully updated from $currentVersion to $newVersion!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Version appears unchanged. You may need to restart PowerShell." -ForegroundColor Yellow
    }
    
    # Clean up temp file
    Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "❌ Error downloading or installing:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual update instructions:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://cli.scalingo.com/install" -ForegroundColor Cyan
    Write-Host "2. Or visit: https://github.com/Scalingo/cli/releases/latest" -ForegroundColor Cyan
    Write-Host "3. Download 'scalingo_windows_amd64.exe'" -ForegroundColor Cyan
    Write-Host "4. Replace the file at: $scalingoPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use Chocolatey (requires admin):" -ForegroundColor Yellow
    Write-Host "   choco upgrade scalingo-cli -y" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

