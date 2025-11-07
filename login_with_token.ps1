# Login to Scalingo with API Token
# This script helps you login with API token

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Login to Scalingo with API Token" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Add to PATH
$env:Path += ";$env:USERPROFILE\AppData\Local\Programs\Scalingo"

Write-Host "Step 1: Get API Token from Dashboard" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://dashboard.scalingo.com" -ForegroundColor Cyan
Write-Host "2. Login with:" -ForegroundColor Cyan
Write-Host "   Email: aliasadi3853@gmail.com" -ForegroundColor Gray
Write-Host "   Password: Aasadi2233#" -ForegroundColor Gray
Write-Host "3. Go to: Account → API Tokens" -ForegroundColor Cyan
Write-Host "   Or: https://dashboard.scalingo.com/account/tokens" -ForegroundColor Gray
Write-Host "4. Click 'Create a new token'" -ForegroundColor Cyan
Write-Host "5. Give it a name (e.g., 'migration-token')" -ForegroundColor Cyan
Write-Host "6. Copy the token (it's shown only once!)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Enter when you have the token..." -ForegroundColor Yellow
Read-Host

Write-Host ""
Write-Host "Step 2: Login with API Token" -ForegroundColor Yellow
Write-Host ""
Write-Host "Running: scalingo login --api-token" -ForegroundColor Cyan
Write-Host "Paste your API token when prompted" -ForegroundColor Yellow
Write-Host ""

scalingo login --api-token

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Login successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check login
    Write-Host "Checking login status..." -ForegroundColor Yellow
    scalingo whoami
    
    Write-Host ""
    Write-Host "Now you can run migration:" -ForegroundColor Green
    Write-Host "scalingo --app mywebsite run python manage.py migrate accounts" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Login failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. API token is correct" -ForegroundColor Cyan
    Write-Host "2. Token is not expired" -ForegroundColor Cyan
    Write-Host "3. Try creating a new token" -ForegroundColor Cyan
}

