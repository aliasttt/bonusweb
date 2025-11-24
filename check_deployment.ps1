# Script to check if deployment is complete and psycopg2 is installed

$appName = "mywebsite"

Write-Host "Checking deployment status..." -ForegroundColor Cyan

# Check latest deployment
$deployments = scalingo --app $appName deployments 2>&1 | Out-String
if ($deployments -match "success.*b8089bb") {
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
} elseif ($deployments -match "starting.*b8089bb") {
    Write-Host "⏳ Deployment still in progress..." -ForegroundColor Yellow
    Write-Host "Please wait a few more minutes and try again." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "⚠️  Could not determine deployment status" -ForegroundColor Yellow
}

Write-Host "`nTesting psycopg2 installation..." -ForegroundColor Cyan

# Create a temporary test file
$testFile = "test_psycopg2.py"
@"
try:
    import psycopg2
    print('SUCCESS: psycopg2 is installed!')
except ImportError:
    print('ERROR: psycopg2 is NOT installed')
"@ | Out-File -FilePath $testFile -Encoding UTF8

# Test in Scalingo
$result = scalingo --app $appName run python $testFile 2>&1

if ($result -match "SUCCESS") {
    Write-Host "✅ psycopg2 is installed!" -ForegroundColor Green
    Write-Host "`nYou can now run:" -ForegroundColor Cyan
    Write-Host "1. scalingo --app $appName run python manage.py migrate" -ForegroundColor White
    Write-Host "2. scalingo --app $appName run python manage.py createsuperuser" -ForegroundColor White
} else {
    Write-Host "❌ psycopg2 is NOT installed yet" -ForegroundColor Red
    Write-Host "Please wait for deployment to complete." -ForegroundColor Yellow
}

# Clean up
Remove-Item $testFile -ErrorAction SilentlyContinue



