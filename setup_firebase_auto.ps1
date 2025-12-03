# اسکریپت خودکار برای تنظیم Firebase Credentials در Scalingo
# این اسکریپت به صورت خودکار فایل JSON را می‌خواند و در Scalingo تنظیم می‌کند

$APP_NAME = "mywebsite"  # نام اپلیکیشن خود را اینجا وارد کنید

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "تنظیم خودکار Firebase Credentials" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# بررسی Scalingo CLI
Write-Host "بررسی Scalingo CLI..." -ForegroundColor Yellow
try {
    $scalingoVersion = scalingo --version 2>&1
    Write-Host "✅ Scalingo CLI نصب است" -ForegroundColor Green
} catch {
    Write-Host "❌ Scalingo CLI نصب نیست!" -ForegroundColor Red
    Write-Host "   لطفاً از https://cli.scalingo.com/install دانلود کنید" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# لاگین به Scalingo
Write-Host "لاگین به Scalingo..." -ForegroundColor Yellow
scalingo login
Write-Host ""

# جستجوی فایل JSON
Write-Host "جستجوی فایل Firebase Service Account JSON..." -ForegroundColor Yellow

$possiblePaths = @(
    "service-account.json",
    "firebase-service-account.json",
    "firebase-credentials.json",
    ".\service-account.json",
    ".\firebase-service-account.json"
)

$jsonFile = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $jsonFile = $path
        Write-Host "✅ فایل یافت شد: $path" -ForegroundColor Green
        break
    }
}

if (-not $jsonFile) {
    Write-Host ""
    Write-Host "⚠️  فایل JSON یافت نشد!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "لطفاً مسیر فایل Firebase Service Account JSON را وارد کنید:" -ForegroundColor White
    $jsonFile = Read-Host "مسیر فایل"
    
    if (-not (Test-Path $jsonFile)) {
        Write-Host ""
        Write-Host "❌ فایل یافت نشد: $jsonFile" -ForegroundColor Red
        Write-Host ""
        Write-Host "برای دریافت فایل:" -ForegroundColor Yellow
        Write-Host "1. به https://console.firebase.google.com بروید" -ForegroundColor White
        Write-Host "2. پروژه خود را انتخاب کنید" -ForegroundColor White
        Write-Host "3. Settings → Project settings → Service accounts" -ForegroundColor White
        Write-Host "4. Generate new private key را کلیک کنید" -ForegroundColor White
        exit 1
    }
}

Write-Host ""
Write-Host "خواندن و تبدیل فایل به Base64..." -ForegroundColor Yellow

try {
    $jsonContent = Get-Content $jsonFile -Raw -Encoding UTF8
    
    # بررسی اینکه JSON معتبر است
    try {
        $jsonObject = $jsonContent | ConvertFrom-Json
        Write-Host "✅ JSON معتبر است" -ForegroundColor Green
    } catch {
        Write-Host "❌ JSON معتبر نیست!" -ForegroundColor Red
        exit 1
    }
    
    # تبدیل به Base64
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonContent)
    $base64 = [System.Convert]::ToBase64String($bytes)
    
    Write-Host "✅ فایل با موفقیت تبدیل شد" -ForegroundColor Green
    Write-Host ""
    
    # تنظیم در Scalingo
    Write-Host "تنظیم FIREBASE_CREDENTIALS_BASE64 در Scalingo..." -ForegroundColor Yellow
    Write-Host "   App: $APP_NAME" -ForegroundColor Gray
    
    $result = scalingo --app $APP_NAME env-set "FIREBASE_CREDENTIALS_BASE64=$base64" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Firebase Credentials با موفقیت تنظیم شد!" -ForegroundColor Green
    } else {
        Write-Host "❌ خطا در تنظیم credentials: $result" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    
    # بررسی تنظیمات
    Write-Host "بررسی تنظیمات..." -ForegroundColor Yellow
    $envVars = scalingo --app $APP_NAME env 2>&1 | Select-String "FIREBASE"
    
    if ($envVars) {
        Write-Host "✅ متغیرهای Firebase:" -ForegroundColor Green
        $envVars | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    } else {
        Write-Host "⚠️  متغیرهای Firebase یافت نشد!" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ تنظیمات کامل شد!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "مراحل بعدی:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Restart اپلیکیشن:" -ForegroundColor White
    Write-Host "   scalingo --app $APP_NAME restart" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. بررسی لاگ‌ها:" -ForegroundColor White
    Write-Host "   scalingo --app $APP_NAME logs --follow" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. تست Push Notification:" -ForegroundColor White
    Write-Host "   به /partners/notifications/ بروید" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ خطا: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

