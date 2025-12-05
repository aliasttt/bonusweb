# Script to fix Firebase and FCM environment variables in Scalingo
# This script helps remove placeholder values and set correct configuration

$APP_NAME = "mywebsite"  # Change this to your Scalingo app name

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Firebase/FCM Environment Variables" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Scalingo CLI is available
Write-Host "Checking Scalingo CLI..." -ForegroundColor Yellow
try {
    $scalingoVersion = scalingo --version 2>&1
    Write-Host "✅ Scalingo CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Scalingo CLI is not installed!" -ForegroundColor Red
    Write-Host "   Please install from: https://cli.scalingo.com/install" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Checking current environment variables..." -ForegroundColor Yellow
Write-Host ""

# Check current Firebase credentials
$currentFile = scalingo --app $APP_NAME env | Select-String "FIREBASE_CREDENTIALS_FILE"
$currentJson = scalingo --app $APP_NAME env | Select-String "FIREBASE_CREDENTIALS_JSON"
$currentBase64 = scalingo --app $APP_NAME env | Select-String "FIREBASE_CREDENTIALS_BASE64"
$currentFcmKey = scalingo --app $APP_NAME env | Select-String "FCM_SERVER_KEY"

Write-Host "Current values:" -ForegroundColor Cyan
if ($currentFile) {
    Write-Host "  FIREBASE_CREDENTIALS_FILE: $($currentFile.ToString().Split('=')[1])" -ForegroundColor Gray
}
if ($currentJson) {
    Write-Host "  FIREBASE_CREDENTIALS_JSON: [SET]" -ForegroundColor Gray
}
if ($currentBase64) {
    Write-Host "  FIREBASE_CREDENTIALS_BASE64: [SET]" -ForegroundColor Gray
}
if ($currentFcmKey) {
    Write-Host "  FCM_SERVER_KEY: [SET]" -ForegroundColor Gray
} else {
    Write-Host "  FCM_SERVER_KEY: [NOT SET]" -ForegroundColor Red
}

Write-Host ""

# Check if FIREBASE_CREDENTIALS_FILE is set to placeholder
if ($currentFile -and $currentFile.ToString() -match "/path/to/") {
    Write-Host "⚠️  Found placeholder path in FIREBASE_CREDENTIALS_FILE" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Do you want to unset FIREBASE_CREDENTIALS_FILE? (Y/N)" -ForegroundColor White
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host "Unsetting FIREBASE_CREDENTIALS_FILE..." -ForegroundColor Yellow
        scalingo --app $APP_NAME env-unset "FIREBASE_CREDENTIALS_FILE"
        Write-Host "✅ Unset FIREBASE_CREDENTIALS_FILE" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Firebase credentials are configured
if (-not $currentBase64 -and -not $currentJson) {
    Write-Host "❌ Firebase credentials are not configured!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To configure Firebase credentials:" -ForegroundColor Yellow
    Write-Host "1. Get your Firebase service account JSON file from:" -ForegroundColor White
    Write-Host "   https://console.firebase.google.com → Project Settings → Service Accounts" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Convert to Base64 (recommended method):" -ForegroundColor White
    Write-Host '   $json = Get-Content "service-account.json" -Raw' -ForegroundColor Cyan
    Write-Host '   $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)' -ForegroundColor Cyan
    Write-Host '   $base64 = [System.Convert]::ToBase64String($bytes)' -ForegroundColor Cyan
    Write-Host '   Write-Host $base64' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Set in Scalingo:" -ForegroundColor White
    Write-Host "   scalingo --app $APP_NAME env-set `"FIREBASE_CREDENTIALS_BASE64=<BASE64_STRING>`"" -ForegroundColor Cyan
    Write-Host ""
}

# Check if FCM_SERVER_KEY is configured
if (-not $currentFcmKey) {
    Write-Host "❌ FCM_SERVER_KEY is not configured!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To configure FCM_SERVER_KEY:" -ForegroundColor Yellow
    Write-Host "1. Get your FCM Server Key from:" -ForegroundColor White
    Write-Host "   https://console.firebase.google.com → Project Settings → Cloud Messaging" -ForegroundColor Gray
    Write-Host "   Look for 'Server key' or 'Legacy server key'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Set in Scalingo:" -ForegroundColor White
    Write-Host "   scalingo --app $APP_NAME env-set `"FCM_SERVER_KEY=<YOUR_SERVER_KEY>`"" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Note: FCM_SERVER_KEY is used as a fallback when Firebase Admin SDK is not available." -ForegroundColor Gray
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "After setting environment variables:" -ForegroundColor Yellow
Write-Host "1. Restart your app:" -ForegroundColor White
Write-Host "   scalingo --app $APP_NAME restart" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Check logs:" -ForegroundColor White
Write-Host "   scalingo --app $APP_NAME logs --follow" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Verify Firebase is initialized (look for 'Firebase Admin SDK initialized successfully')" -ForegroundColor White
Write-Host ""

