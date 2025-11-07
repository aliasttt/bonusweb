# اسکریپت کامل: نصب Scalingo CLI و اجرای Migration
# این اسکریپت Scalingo CLI را دانلود، نصب و migration را اجرا می‌کند

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "نصب Scalingo CLI و اجرای Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# بررسی نصب بودن Scalingo CLI
Write-Host "بررسی نصب بودن Scalingo CLI..." -ForegroundColor Yellow
try {
    $scalingoVersion = scalingo --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Scalingo CLI نصب است" -ForegroundColor Green
        Write-Host "   Version: $scalingoVersion" -ForegroundColor Gray
        $cliInstalled = $true
    }
} catch {
    $cliInstalled = $false
}

# اگر نصب نیست، نصب می‌کنیم
if (-not $cliInstalled) {
    Write-Host "❌ Scalingo CLI نصب نیست" -ForegroundColor Red
    Write-Host ""
    Write-Host "در حال دانلود و نصب Scalingo CLI..." -ForegroundColor Yellow
    Write-Host ""
    
    # دانلود Scalingo CLI برای Windows
    $downloadUrl = "https://github.com/Scalingo/cli/releases/latest/download/scalingo_windows_amd64.exe"
    $installPath = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\scalingo.exe"
    $tempPath = "$env:TEMP\scalingo.exe"
    
    try {
        Write-Host "دانلود Scalingo CLI..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $downloadUrl -OutFile $tempPath -UseBasicParsing
        
        Write-Host "نصب Scalingo CLI..." -ForegroundColor Yellow
        # کپی به مسیر مناسب
        Copy-Item $tempPath $installPath -Force
        
        # Add to PATH if needed
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($currentPath -notlike "*WindowsApps*") {
            $windowsAppsPath = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$windowsAppsPath", "User")
        }
        
        Write-Host "✅ Scalingo CLI نصب شد!" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  لطفاً PowerShell را restart کنید تا تغییرات PATH اعمال شود." -ForegroundColor Yellow
        Write-Host "یا دستور زیر را اجرا کنید:" -ForegroundColor Cyan
        Write-Host "`$env:Path += `";$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps`"" -ForegroundColor Gray
        Write-Host ""
        
        # اضافه کردن به PATH فعلی session
        $env:Path += ";$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"
        
        # بررسی دوباره
        Start-Sleep -Seconds 2
        try {
            $scalingoVersion = scalingo --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Scalingo CLI آماده است!" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️  لطفاً PowerShell را restart کنید و دوباره این اسکریپت را اجرا کنید." -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "❌ خطا در دانلود/نصب Scalingo CLI" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "لطفاً به صورت دستی نصب کنید:" -ForegroundColor Yellow
        Write-Host "1. به آدرس زیر بروید: https://cli.scalingo.com/install" -ForegroundColor Cyan
        Write-Host "2. فایل نصب را دانلود و اجرا کنید" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host ""

# بررسی لاگین بودن
Write-Host "بررسی لاگین بودن در Scalingo..." -ForegroundColor Yellow
try {
    $whoami = scalingo whoami 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ شما لاگین هستید" -ForegroundColor Green
        Write-Host "   $whoami" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  شما لاگین نیستید" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "لطفاً لاگین کنید:" -ForegroundColor Cyan
        Write-Host "scalingo login" -ForegroundColor Gray
        Write-Host ""
        Write-Host "در حال باز کردن مرورگر برای لاگین..." -ForegroundColor Yellow
        scalingo login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ خطا در لاگین" -ForegroundColor Red
            Write-Host "لطفاً دستور 'scalingo login' را به صورت دستی اجرا کنید." -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "❌ خطا در بررسی لاگین" -ForegroundColor Red
    Write-Host "لطفاً دستور 'scalingo login' را به صورت دستی اجرا کنید." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# نام اپلیکیشن
$appName = "mywebsite"
Write-Host "نام اپلیکیشن: $appName" -ForegroundColor Cyan
Write-Host ""

# بررسی وضعیت migration ها
Write-Host "بررسی وضعیت migration ها..." -ForegroundColor Yellow
try {
    $migrations = scalingo --app $appName run python manage.py showmigrations accounts 2>&1
    Write-Host $migrations
} catch {
    Write-Host "⚠️  نتوانست وضعیت migration ها را بررسی کند" -ForegroundColor Yellow
}

Write-Host ""

# اجرای migration
Write-Host "در حال اجرای migration..." -ForegroundColor Yellow
Write-Host "این ممکن است چند لحظه طول بکشد..." -ForegroundColor Gray
Write-Host ""

try {
    $result = scalingo --app $appName run python manage.py migrate accounts 2>&1
    Write-Host $result
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Migration با موفقیت اجرا شد!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ خطا در اجرای migration" -ForegroundColor Red
        Write-Host "لطفاً لاگ‌ها را بررسی کنید:" -ForegroundColor Yellow
        Write-Host "scalingo --app $appName logs" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "❌ خطا در اجرای migration" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ تمام!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

