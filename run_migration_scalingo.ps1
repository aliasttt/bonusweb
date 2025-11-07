# اسکریپت اجرای Migration در Scalingo
# این اسکریپت Scalingo CLI را بررسی می‌کند و migration را اجرا می‌کند

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "اجرای Migration در Scalingo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# بررسی نصب بودن Scalingo CLI
Write-Host "بررسی نصب بودن Scalingo CLI..." -ForegroundColor Yellow
try {
    $scalingoVersion = scalingo --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Scalingo CLI نصب است" -ForegroundColor Green
        Write-Host "   Version: $scalingoVersion" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Scalingo CLI نصب نیست" -ForegroundColor Red
    Write-Host ""
    Write-Host "لطفاً Scalingo CLI را نصب کنید:" -ForegroundColor Yellow
    Write-Host "1. دانلود از: https://cli.scalingo.com/install" -ForegroundColor Cyan
    Write-Host "2. یا استفاده از Chocolatey: choco install scalingo-cli" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "بعد از نصب، این اسکریپت را دوباره اجرا کنید." -ForegroundColor Yellow
    exit 1
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
        Write-Host "در حال لاگین..." -ForegroundColor Yellow
        scalingo login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ خطا در لاگین" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ خطا در بررسی لاگین" -ForegroundColor Red
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

