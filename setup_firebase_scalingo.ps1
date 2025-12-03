# اسکریپت PowerShell برای تنظیم Firebase Credentials در Scalingo
# Usage: .\setup_firebase_scalingo.ps1

$APP_NAME = "mywebsite"  # نام اپلیکیشن خود را اینجا وارد کنید

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "تنظیم Firebase Credentials در Scalingo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# بررسی لاگین
Write-Host "1. بررسی لاگین Scalingo..." -ForegroundColor Yellow
scalingo login
Write-Host ""

Write-Host "2. انتخاب روش تنظیم Firebase Credentials:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   روش 1: استفاده از فایل JSON (توصیه می‌شود)" -ForegroundColor Green
Write-Host "   روش 2: استفاده از JSON string" -ForegroundColor Green
Write-Host "   روش 3: استفاده از Base64 encoded" -ForegroundColor Green
Write-Host ""

$method = Read-Host "روش را انتخاب کنید (1/2/3)"

switch ($method) {
    "1" {
        Write-Host ""
        Write-Host "روش 1: استفاده از فایل JSON" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚠️  توجه: Scalingo نمی‌تواند مستقیماً فایل را بخواند" -ForegroundColor Yellow
        Write-Host "   باید محتوای فایل را به صورت Base64 یا JSON string تنظیم کنید" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "لطفاً مسیر فایل JSON را وارد کنید:" -ForegroundColor White
        $filePath = Read-Host "مسیر فایل"
        
        if (Test-Path $filePath) {
            Write-Host ""
            Write-Host "خواندن فایل و تبدیل به Base64..." -ForegroundColor Yellow
            $jsonContent = Get-Content $filePath -Raw
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonContent)
            $base64 = [System.Convert]::ToBase64String($bytes)
            
            Write-Host ""
            Write-Host "تنظیم FIREBASE_CREDENTIALS_BASE64..." -ForegroundColor Yellow
            scalingo --app $APP_NAME env-set "FIREBASE_CREDENTIALS_BASE64=$base64"
            
            Write-Host ""
            Write-Host "✅ Firebase Credentials با موفقیت تنظیم شد!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "❌ فایل یافت نشد!" -ForegroundColor Red
            exit 1
        }
    }
    "2" {
        Write-Host ""
        Write-Host "روش 2: استفاده از JSON string" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚠️  توجه: JSON باید در یک خط باشد و تمام escape characters درست باشند" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "لطفاً محتوای JSON را وارد کنید (یا Enter برای خواندن از فایل):" -ForegroundColor White
        $jsonInput = Read-Host "JSON"
        
        if ([string]::IsNullOrWhiteSpace($jsonInput)) {
            Write-Host ""
            Write-Host "لطفاً مسیر فایل JSON را وارد کنید:" -ForegroundColor White
            $filePath = Read-Host "مسیر فایل"
            
            if (Test-Path $filePath) {
                $jsonContent = Get-Content $filePath -Raw
            } else {
                Write-Host ""
                Write-Host "❌ فایل یافت نشد!" -ForegroundColor Red
                exit 1
            }
        } else {
            $jsonContent = $jsonInput
        }
        
        # Escape quotes برای PowerShell
        $escapedJson = $jsonContent -replace '"', '\"'
        
        Write-Host ""
        Write-Host "تنظیم FIREBASE_CREDENTIALS_JSON..." -ForegroundColor Yellow
        scalingo --app $APP_NAME env-set "FIREBASE_CREDENTIALS_JSON=$escapedJson"
        
        Write-Host ""
        Write-Host "✅ Firebase Credentials با موفقیت تنظیم شد!" -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "روش 3: استفاده از Base64 encoded" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "لطفاً Base64 string را وارد کنید (یا Enter برای خواندن از فایل):" -ForegroundColor White
        $base64Input = Read-Host "Base64"
        
        if ([string]::IsNullOrWhiteSpace($base64Input)) {
            Write-Host ""
            Write-Host "لطفاً مسیر فایل JSON را وارد کنید:" -ForegroundColor White
            $filePath = Read-Host "مسیر فایل"
            
            if (Test-Path $filePath) {
                Write-Host ""
                Write-Host "خواندن فایل و تبدیل به Base64..." -ForegroundColor Yellow
                $jsonContent = Get-Content $filePath -Raw
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonContent)
                $base64 = [System.Convert]::ToBase64String($bytes)
            } else {
                Write-Host ""
                Write-Host "❌ فایل یافت نشد!" -ForegroundColor Red
                exit 1
            }
        } else {
            $base64 = $base64Input
        }
        
        Write-Host ""
        Write-Host "تنظیم FIREBASE_CREDENTIALS_BASE64..." -ForegroundColor Yellow
        scalingo --app $APP_NAME env-set "FIREBASE_CREDENTIALS_BASE64=$base64"
        
        Write-Host ""
        Write-Host "✅ Firebase Credentials با موفقیت تنظیم شد!" -ForegroundColor Green
    }
    default {
        Write-Host ""
        Write-Host "❌ روش نامعتبر!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "بررسی تنظیمات" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "بررسی متغیرهای محیطی..." -ForegroundColor Yellow
scalingo --app $APP_NAME env | Select-String "FIREBASE"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "نکات مهم:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. بعد از تنظیم credentials، باید اپلیکیشن را restart کنید:" -ForegroundColor Yellow
Write-Host "   scalingo --app $APP_NAME restart" -ForegroundColor White
Write-Host ""
Write-Host "2. برای تست، می‌توانید از پنل ادمین notification بفرستید:" -ForegroundColor Yellow
Write-Host "   /partners/notifications/" -ForegroundColor White
Write-Host ""
Write-Host "3. برای بررسی لاگ‌ها:" -ForegroundColor Yellow
Write-Host "   scalingo --app $APP_NAME logs --follow" -ForegroundColor White
Write-Host ""

