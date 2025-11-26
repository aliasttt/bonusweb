# PowerShell script to add PostgreSQL database to Scalingo app
# Usage: .\setup_database_scalingo.ps1

param(
    [string]$AppName = "mywebsite"
)

Write-Host "Setting up PostgreSQL database for Scalingo app: $AppName" -ForegroundColor Cyan

# Check if app name is provided
if (-not $AppName) {
    Write-Host "Error: App name is required!" -ForegroundColor Red
    Write-Host "Usage: .\setup_database_scalingo.ps1 -AppName 'mywebsite'" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nStep 1: Adding PostgreSQL addon (sandbox plan - FREE)..." -ForegroundColor Yellow
scalingo --app $AppName addons-add postgresql:postgresql-sandbox

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL addon added successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to add PostgreSQL addon" -ForegroundColor Red
    exit 1
}

Write-Host "`nStep 2: Waiting for database to be ready (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`nStep 3: Checking DATABASE_URL environment variable..." -ForegroundColor Yellow
$dbUrl = scalingo --app $AppName env | Select-String "DATABASE_URL"

if ($dbUrl) {
    Write-Host "✅ DATABASE_URL is set:" -ForegroundColor Green
    Write-Host $dbUrl -ForegroundColor Cyan
} else {
    Write-Host "⚠️  DATABASE_URL not found. It should be set automatically by Scalingo." -ForegroundColor Yellow
}

Write-Host "`nStep 4: Running migrations..." -ForegroundColor Yellow
Write-Host "Running: scalingo --app $AppName run python manage.py migrate" -ForegroundColor Cyan
scalingo --app $AppName run python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migrations completed successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Migration had some issues. Check the output above." -ForegroundColor Yellow
}

Write-Host "`nStep 5: Restarting application..." -ForegroundColor Yellow
scalingo --app $AppName restart

Write-Host "`n✅ Database setup complete!" -ForegroundColor Green
Write-Host "`nImportant Notes:" -ForegroundColor Yellow
Write-Host "1. Your database is now persistent - data won't be lost on deployment" -ForegroundColor White
Write-Host "2. User registrations will persist across deployments" -ForegroundColor White
Write-Host "3. All your data (users, products, reviews, etc.) is now safe!" -ForegroundColor White
Write-Host "`n⚠️  IMPORTANT: You need to re-register your business and users since the old SQLite database was lost." -ForegroundColor Red






