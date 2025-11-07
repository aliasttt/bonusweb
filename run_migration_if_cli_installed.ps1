# Run Migration Script (if CLI is installed)
# This script runs migration if Scalingo CLI is already installed

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Migration in Scalingo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Scalingo CLI is installed
Write-Host "Checking Scalingo CLI..." -ForegroundColor Yellow
$cliFound = $false
$cliPath = $null

# Check common paths
$possiblePaths = @(
    "$env:USERPROFILE\AppData\Local\Programs\Scalingo\scalingo.exe",
    "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\scalingo.exe",
    "C:\Program Files\Scalingo\scalingo.exe",
    "C:\Program Files (x86)\Scalingo\scalingo.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $cliPath = $path
        $cliFound = $true
        Write-Host "Found Scalingo CLI at: $path" -ForegroundColor Green
        break
    }
}

# Check if in PATH
if (-not $cliFound) {
    try {
        $null = Get-Command scalingo -ErrorAction Stop
        $cliFound = $true
        Write-Host "Scalingo CLI found in PATH" -ForegroundColor Green
    } catch {
        Write-Host "Scalingo CLI not found!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Scalingo CLI first:" -ForegroundColor Yellow
        Write-Host "1. Download from: https://cli.scalingo.com/install" -ForegroundColor Cyan
        Write-Host "2. Or use Dashboard method (see MIGRATE_NOW.md)" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host ""

# Check login
Write-Host "Checking login status..." -ForegroundColor Yellow
$isLoggedIn = $false

try {
    if ($cliPath) {
        $whoami = & $cliPath whoami 2>&1
    } else {
        $whoami = scalingo whoami 2>&1
    }
    
    if ($LASTEXITCODE -eq 0 -and $whoami -notmatch "error" -and $whoami -notmatch "not logged") {
        $isLoggedIn = $true
        Write-Host "Logged in as: $whoami" -ForegroundColor Green
    }
} catch {
    $isLoggedIn = $false
}

if (-not $isLoggedIn) {
    Write-Host "Not logged in. Please login first:" -ForegroundColor Yellow
    Write-Host ""
    if ($cliPath) {
        Write-Host "$cliPath login" -ForegroundColor Cyan
        & $cliPath login
    } else {
        Write-Host "scalingo login" -ForegroundColor Cyan
        scalingo login
    }
    
    Start-Sleep -Seconds 3
    
    # Verify login
    try {
        if ($cliPath) {
            $whoami = & $cliPath whoami 2>&1
        } else {
            $whoami = scalingo whoami 2>&1
        }
        if ($LASTEXITCODE -eq 0) {
            $isLoggedIn = $true
            Write-Host "Login successful!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Login verification failed. Please try again." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# App name
$appName = "mywebsite"
Write-Host "App name: $appName" -ForegroundColor Cyan
Write-Host ""

# Check migration status
Write-Host "Checking migration status..." -ForegroundColor Yellow
try {
    if ($cliPath) {
        $migrations = & $cliPath --app $appName run python manage.py showmigrations accounts 2>&1
    } else {
        $migrations = scalingo --app $appName run python manage.py showmigrations accounts 2>&1
    }
    Write-Host $migrations
} catch {
    Write-Host "Could not check migration status (continuing anyway)" -ForegroundColor Yellow
}

Write-Host ""

# Run migration
Write-Host "Running migration..." -ForegroundColor Yellow
Write-Host "Command: python manage.py migrate accounts" -ForegroundColor Gray
Write-Host ""

try {
    if ($cliPath) {
        $result = & $cliPath --app $appName run python manage.py migrate accounts 2>&1
    } else {
        $result = scalingo --app $appName run python manage.py migrate accounts 2>&1
    }
    
    Write-Host $result
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "SUCCESS! Migration completed!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Migration completed with warnings" -ForegroundColor Yellow
        Write-Host "Check output above for details" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Cyan
    }
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Error running migration" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs with:" -ForegroundColor Yellow
    if ($cliPath) {
        Write-Host "$cliPath --app $appName logs" -ForegroundColor Cyan
    } else {
        Write-Host "scalingo --app $appName logs" -ForegroundColor Cyan
    }
    Write-Host "========================================" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

