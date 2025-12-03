# اسکریپت PowerShell برای تست کش تصاویر در Scalingo
# Usage: .\test_scalingo_images.ps1

$APP_NAME = "mywebsite"  # نام اپلیکیشن خود را اینجا وارد کنید

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "تست کش تصاویر در Scalingo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# بررسی لاگین
Write-Host "1. بررسی لاگین Scalingo..." -ForegroundColor Yellow
scalingo login
Write-Host ""

# تست کش تصاویر
Write-Host "2. تست کش تصاویر..." -ForegroundColor Yellow
scalingo --app $APP_NAME run python test_image_cache_scalingo.py
Write-Host ""

# بررسی تعداد کش‌ها
Write-Host "3. بررسی تعداد کش‌ها..." -ForegroundColor Yellow
scalingo --app $APP_NAME run python manage.py shell -c "from loyalty.models import ImageCache; print(f'Total cached images: {ImageCache.objects.count()}')"
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "تست کامل شد!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "اگر تصاویر کش نشده‌اند، دستور زیر را اجرا کنید:" -ForegroundColor Yellow
Write-Host "scalingo --app $APP_NAME run python manage.py shell < test_image_cache.py" -ForegroundColor White

