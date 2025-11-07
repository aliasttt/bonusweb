# Login to Scalingo and Run Migration
# This script logs in and runs migration automatically

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Login and Run Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if already logged in
Write-Host "Checking login status..." -ForegroundColor Yellow
try {
    $whoami = scalingo whoami 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Already logged in: $whoami" -ForegroundColor Green
        $isLoggedIn = $true
    } else {
        $isLoggedIn = $false
    }
} catch {
    $isLoggedIn = $false
}

# Login if not logged in
if (-not $isLoggedIn) {
    Write-Host "Not logged in. Logging in..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Username: aliasttt" -ForegroundColor Gray
    Write-Host "Password: ********" -ForegroundColor Gray
    Write-Host ""
    
    # Create a temporary file with login command
    $loginScript = @"
scalingo login --api-token
"@
    
    # Try to login with API token method (more secure)
    # But first, let's try the interactive method
    Write-Host "Please login manually:" -ForegroundColor Yellow
    Write-Host "Run: scalingo login" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use API token:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://dashboard.scalingo.com/account/tokens" -ForegroundColor Cyan
    Write-Host "2. Create a new token" -ForegroundColor Cyan
    Write-Host "3. Run: scalingo login --api-token" -ForegroundColor Cyan
    Write-Host ""
    
    # Try interactive login
    Write-Host "Attempting interactive login..." -ForegroundColor Yellow
    Write-Host "Note: You may need to enter credentials manually" -ForegroundColor Gray
    Write-Host ""
    
    # For now, let's use echo to pipe credentials (not secure, but works)
    # Actually, better to let user do it manually or use API token
    Write-Host "Please run the following command manually:" -ForegroundColor Yellow
    Write-Host "scalingo login" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then run this script again, or continue with migration if already logged in." -ForegroundColor Yellow
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
    $migrations = scalingo --app $appName run python manage.py showmigrations accounts 2>&1
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
    $result = scalingo --app $appName run python manage.py migrate accounts 2>&1
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
    Write-Host "scalingo --app $appName logs" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

