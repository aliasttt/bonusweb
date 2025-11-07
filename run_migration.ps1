# Install and Run Migration Script for Scalingo
# This script installs Scalingo CLI and runs migration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Scalingo Migration Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Scalingo CLI is installed
Write-Host "Checking Scalingo CLI..." -ForegroundColor Yellow
$cliInstalled = $false
try {
    $null = scalingo --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Scalingo CLI is installed" -ForegroundColor Green
        $cliInstalled = $true
    }
} catch {
    $cliInstalled = $false
}

# Install if not installed
if (-not $cliInstalled) {
    Write-Host "Scalingo CLI is not installed" -ForegroundColor Red
    Write-Host "Please install it manually:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://cli.scalingo.com/install" -ForegroundColor Cyan
    Write-Host "2. Download and run the installer" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use the Dashboard method:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://dashboard.scalingo.com" -ForegroundColor Cyan
    Write-Host "2. Select your app: mywebsite" -ForegroundColor Cyan
    Write-Host "3. Go to 'One-off containers' section" -ForegroundColor Cyan
    Write-Host "4. Run: python manage.py migrate accounts" -ForegroundColor Cyan
    exit 1
}

Write-Host ""

# Check login
Write-Host "Checking login status..." -ForegroundColor Yellow
try {
    $whoami = scalingo whoami 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "You are logged in" -ForegroundColor Green
    } else {
        Write-Host "You are not logged in" -ForegroundColor Yellow
        Write-Host "Please run: scalingo login" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "Error checking login" -ForegroundColor Red
    Write-Host "Please run: scalingo login" -ForegroundColor Cyan
    exit 1
}

Write-Host ""

# App name
$appName = "mywebsite"
Write-Host "App name: $appName" -ForegroundColor Cyan
Write-Host ""

# Check migration status
Write-Host "Checking migration status..." -ForegroundColor Yellow
try {
    scalingo --app $appName run python manage.py showmigrations accounts
} catch {
    Write-Host "Could not check migration status" -ForegroundColor Yellow
}

Write-Host ""

# Run migration
Write-Host "Running migration..." -ForegroundColor Yellow
Write-Host "This may take a few moments..." -ForegroundColor Gray
Write-Host ""

try {
    scalingo --app $appName run python manage.py migrate accounts
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Migration completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Error running migration" -ForegroundColor Red
        Write-Host "Check logs with: scalingo --app $appName logs" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "Error running migration" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

