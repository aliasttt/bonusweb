# PowerShell script to create superuser in Scalingo
# Usage: .\create_superuser_scalingo.ps1 -Username "admin" -Email "admin@example.com"

param(
    [string]$AppName = "mywebsite",
    [string]$Username = "admin",
    [string]$Email = "admin@example.com"
)

Write-Host "Creating superuser for Scalingo app: $AppName" -ForegroundColor Cyan

# Check if deployment is complete
Write-Host "`nStep 1: Checking if psycopg2 is installed..." -ForegroundColor Yellow
$checkResult = scalingo --app $AppName run python -c "import psycopg2; print('OK')" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  psycopg2 not installed yet. Waiting for deployment to complete..." -ForegroundColor Yellow
    Write-Host "Please wait for deployment to finish, then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ psycopg2 is installed!" -ForegroundColor Green

# Run migrations
Write-Host "`nStep 2: Running migrations..." -ForegroundColor Yellow
scalingo --app $AppName run python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Migration failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Migrations completed!" -ForegroundColor Green

# Create superuser
Write-Host "`nStep 3: Creating superuser..." -ForegroundColor Yellow
Write-Host "Username: $Username" -ForegroundColor Cyan
Write-Host "Email: $Email" -ForegroundColor Cyan
Write-Host "`nYou will be prompted to enter a password." -ForegroundColor Yellow

# Use Django's createsuperuser command
# Note: This will prompt for password interactively
scalingo --app $AppName run python manage.py createsuperuser --username $Username --email $Email --noinput

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Superuser created successfully!" -ForegroundColor Green
    Write-Host "`n⚠️  Note: If password was not set, you can reset it using:" -ForegroundColor Yellow
    Write-Host "scalingo --app $AppName run python manage.py changepassword $Username" -ForegroundColor Cyan
} else {
    Write-Host "`n⚠️  Superuser might already exist. Trying interactive mode..." -ForegroundColor Yellow
    Write-Host "Run this command manually:" -ForegroundColor Cyan
    Write-Host "scalingo --app $AppName run python manage.py createsuperuser" -ForegroundColor White
}











