# Script to convert Firebase Service Account JSON to Base64 and set in Scalingo

$APP_NAME = "mywebsite"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting FIREBASE_CREDENTIALS_BASE64" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for service-account.json file
$jsonFiles = @(
    "service-account.json",
    "firebase-service-account.json",
    ".\service-account.json",
    ".\firebase-service-account.json"
)

$jsonFile = $null
foreach ($file in $jsonFiles) {
    if (Test-Path $file) {
        $jsonFile = $file
        break
    }
}

if (-not $jsonFile) {
    Write-Host "File service-account.json not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Go to https://console.firebase.google.com" -ForegroundColor White
    Write-Host "2. Select your project" -ForegroundColor White
    Write-Host "3. Settings -> Project settings -> Service accounts" -ForegroundColor White
    Write-Host "4. Click 'Generate new private key'" -ForegroundColor White
    Write-Host "5. Download the JSON file" -ForegroundColor White
    Write-Host "6. Place the file in this folder (service-account.json)" -ForegroundColor White
    Write-Host ""
    Write-Host "Or enter the file path:" -ForegroundColor Yellow
    $customPath = Read-Host "JSON file path"
    if (Test-Path $customPath) {
        $jsonFile = $customPath
    } else {
        Write-Host "File not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "File found: $jsonFile" -ForegroundColor Green
Write-Host ""

# Read and convert to Base64
Write-Host "Converting to Base64..." -ForegroundColor Yellow
try {
    $jsonContent = Get-Content $jsonFile -Raw -Encoding UTF8
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonContent)
    $base64 = [System.Convert]::ToBase64String($bytes)
    
    Write-Host "Conversion successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Base64 length: $($base64.Length) characters" -ForegroundColor Gray
    Write-Host ""
    
    # Show first 50 characters for confirmation
    Write-Host "Base64 sample (first 50 characters):" -ForegroundColor Cyan
    $sampleLength = [Math]::Min(50, $base64.Length)
    Write-Host $base64.Substring(0, $sampleLength) -ForegroundColor Gray
    Write-Host "..."
    Write-Host ""
    
    # Ask for confirmation
    Write-Host "Do you want to set this value in Scalingo? (Y/N)" -ForegroundColor Yellow
    $confirm = Read-Host
    
    if ($confirm -eq "Y" -or $confirm -eq "y") {
        Write-Host ""
        Write-Host "Setting in Scalingo..." -ForegroundColor Yellow
        
        # Set in Scalingo
        $envVar = "FIREBASE_CREDENTIALS_BASE64=$base64"
        $result = scalingo --app $APP_NAME env-set $envVar 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "FIREBASE_CREDENTIALS_BASE64 set successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "1. Restart:" -ForegroundColor White
            Write-Host "   scalingo --app $APP_NAME restart" -ForegroundColor Gray
            Write-Host ""
            Write-Host "2. Check logs:" -ForegroundColor White
            Write-Host "   scalingo --app $APP_NAME logs --follow" -ForegroundColor Gray
            Write-Host ""
            Write-Host "3. You should see:" -ForegroundColor White
            Write-Host "   DEBUG: Loading Firebase credentials from FIREBASE_CREDENTIALS_BASE64" -ForegroundColor Green
            Write-Host "   DEBUG: Firebase Admin SDK initialized successfully" -ForegroundColor Green
        } else {
            Write-Host "Error setting variable:" -ForegroundColor Red
            Write-Host $result
        }
    } else {
        Write-Host ""
        Write-Host "Base64 generated. You can set it manually:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "scalingo --app $APP_NAME env-set `"FIREBASE_CREDENTIALS_BASE64=$base64`"" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Or copy the Base64 and set it in Scalingo Dashboard." -ForegroundColor Gray
    }
    
} catch {
    Write-Host "Error converting file:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
