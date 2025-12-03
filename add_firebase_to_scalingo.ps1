# اسکریپت ساده برای اضافه کردن Firebase Credentials به Scalingo
# Usage: .\add_firebase_to_scalingo.ps1

$APP_NAME = "mywebsite"  # نام اپلیکیشن خود را اینجا وارد کنید

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "اضافه کردن Firebase Credentials به Scalingo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# بررسی لاگین
Write-Host "بررسی لاگین Scalingo..." -ForegroundColor Yellow
scalingo login
Write-Host ""

# دریافت مسیر فایل JSON
Write-Host "لطفاً مسیر فایل Firebase Service Account JSON را وارد کنید:" -ForegroundColor White
Write-Host "(یا Enter برای استفاده از مسیر پیش‌فرض: service-account.json)" -ForegroundColor Gray
$filePath = Read-Host "مسیر فایل"

if ([string]::IsNullOrWhiteSpace($filePath)) {
    $filePath = "service-account.json"
}

if (-not (Test-Path $filePath)) {
    Write-Host ""
    Write-Host "❌ فایل یافت نشد: $filePath" -ForegroundColor Red
    Write-Host ""
    Write-Host "لطفاً مسیر کامل فایل را وارد کنید:" -ForegroundColor Yellow
    $filePath = Read-Host "مسیر کامل فایل"
    
    if (-not (Test-Path $filePath)) {
        Write-Host ""
        Write-Host "❌ فایل یافت نشد!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "خواندن فایل و تبدیل به Base64..." -ForegroundColor Yellow

try {
    $jsonContent = Get-Content $filePath -Raw -Encoding UTF8
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonContent)
    $base64 = [System.Convert]::ToBase64String($bytes)
    
    Write-Host "✅ فایل با موفقیت خوانده شد" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "تنظیم FIREBASE_CREDENTIALS_BASE64 در Scalingo..." -ForegroundColor Yellow
    scalingo --app $APP_NAME env-set "FIREBASE_CREDENTIALS_BASE64=$base64"
    
    Write-Host ""
    Write-Host "✅ Firebase Credentials با موفقیت به Scalingo اضافه شد!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "مراحل بعدی:" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Restart اپلیکیشن:" -ForegroundColor Yellow
    Write-Host "   scalingo --app $APP_NAME restart" -ForegroundColor White
    Write-Host ""
    Write-Host "2. بررسی لاگ‌ها:" -ForegroundColor Yellow
    Write-Host "   scalingo --app $APP_NAME logs --follow" -ForegroundColor White
    Write-Host ""
    Write-Host "3. تست Push Notification:" -ForegroundColor Yellow
    Write-Host "   به /partners/notifications/ بروید و یک notification بفرستید" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ خطا: $_" -ForegroundColor Red
    exit 1
}

