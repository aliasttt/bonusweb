# اسکریپت نصب Scalingo CLI برای Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "نصب Scalingo CLI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# بررسی نصب بودن Chocolatey
Write-Host "بررسی نصب بودن Chocolatey..." -ForegroundColor Yellow
try {
    $chocoVersion = choco --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Chocolatey نصب است" -ForegroundColor Green
        Write-Host "   Version: $chocoVersion" -ForegroundColor Gray
        Write-Host ""
        Write-Host "در حال نصب Scalingo CLI با Chocolatey..." -ForegroundColor Yellow
        choco install scalingo-cli -y
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Scalingo CLI با موفقیت نصب شد!" -ForegroundColor Green
            Write-Host ""
            Write-Host "حالا می‌توانید اسکریپت run_migration_scalingo.ps1 را اجرا کنید." -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "❌ خطا در نصب Scalingo CLI" -ForegroundColor Red
            Write-Host ""
            Write-Host "لطفاً به صورت دستی نصب کنید:" -ForegroundColor Yellow
            Write-Host "1. دانلود از: https://cli.scalingo.com/install" -ForegroundColor Cyan
            Write-Host "2. یا از Chocolatey: choco install scalingo-cli" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Chocolatey نصب نیست" -ForegroundColor Red
        Write-Host ""
        Write-Host "لطفاً Scalingo CLI را به صورت دستی نصب کنید:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "روش 1: دانلود مستقیم" -ForegroundColor Cyan
        Write-Host "1. به آدرس زیر بروید: https://cli.scalingo.com/install" -ForegroundColor Gray
        Write-Host "2. فایل نصب را دانلود کنید" -ForegroundColor Gray
        Write-Host "3. فایل را اجرا کنید" -ForegroundColor Gray
        Write-Host ""
        Write-Host "روش 2: نصب Chocolatey و سپس Scalingo CLI" -ForegroundColor Cyan
        Write-Host "1. Chocolatey را نصب کنید: https://chocolatey.org/install" -ForegroundColor Gray
        Write-Host "2. سپس این دستور را اجرا کنید: choco install scalingo-cli" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ خطا در بررسی Chocolatey" -ForegroundColor Red
    Write-Host ""
    Write-Host "لطفاً Scalingo CLI را به صورت دستی نصب کنید:" -ForegroundColor Yellow
    Write-Host "1. دانلود از: https://cli.scalingo.com/install" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

