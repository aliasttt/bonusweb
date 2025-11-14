# راهنمای تنظیم Cloudinary

## اطلاعات Cloudinary شما

- **Cloud Name**: `993373522259225`
- **API Key**: `G0UxjA_EEAJ9T_BMd9LS6WOdnZo`
- **API Secret**: (در فایل اصلی ذخیره شده - برای امنیت اینجا نمایش داده نمی‌شود)

## مراحل تنظیم در Scalingo

### 1. تنظیم متغیرهای محیطی

#### روش 1: استفاده از اسکریپت (پیشنهادی)

**در PowerShell:**
```powershell
.\setup_cloudinary_scalingo.ps1 -ApiSecret "YOUR_API_SECRET" -AppName "your-app-name"
```

اگر git remote تنظیم شده باشد، اسکریپت به صورت خودکار نام اپلیکیشن را تشخیص می‌دهد:
```powershell
.\setup_cloudinary_scalingo.ps1 -ApiSecret "YOUR_API_SECRET"
```

**در Bash/Linux:**
```bash
chmod +x setup_cloudinary_scalingo.sh
./setup_cloudinary_scalingo.sh YOUR_API_SECRET your-app-name
```

#### روش 2: دستی

در ترمینال Scalingo یا از طریق dashboard، این دستورات را اجرا کنید:

```bash
scalingo --app your-app-name env-set USE_CLOUDINARY=1
scalingo --app your-app-name env-set CLOUDINARY_CLOUD_NAME=993373522259225
scalingo --app your-app-name env-set CLOUDINARY_API_KEY=G0UxjA_EEAJ9T_BMd9LS6WOdnZo
scalingo --app your-app-name env-set CLOUDINARY_API_SECRET=YOUR_API_SECRET_HERE
```

**⚠️ مهم**: 
- `your-app-name` را با نام واقعی اپلیکیشن Scalingo خود جایگزین کنید
- API Secret را از فایل اصلی کپی کنید و در دستور بالا جایگزین `YOUR_API_SECRET_HERE` کنید

### 2. بررسی تنظیمات

برای اطمینان از اینکه متغیرها درست تنظیم شده‌اند:

```bash
scalingo --app your-app-name env | grep CLOUDINARY
```

باید این خروجی را ببینید:
```
CLOUDINARY_API_KEY=G0UxjA_EEAJ9T_BMd9LS6WOdnZo
CLOUDINARY_CLOUD_NAME=993373522259225
CLOUDINARY_API_SECRET=**** (hidden)
USE_CLOUDINARY=1
```

### 3. Deploy مجدد

بعد از تنظیم متغیرها، باید اپلیکیشن را restart کنید:

```bash
scalingo --app your-app-name restart
```

یا اگر تغییراتی در کد داده‌اید:

```bash
git add .
git commit -m "Configure Cloudinary for media storage"
git push scalingo main
```

### 4. تست کردن

بعد از deploy، یک فایل جدید آپلود کنید و بررسی کنید که:
- فایل در Cloudinary ذخیره می‌شود
- URL فایل از Cloudinary سرو می‌شود
- فایل بعد از restart هم موجود است

### 5. بررسی فایل‌های موجود

برای بررسی فایل‌های موجود در دیتابیس:

```bash
python check_media_files.py
```

یا در Scalingo:

```bash
scalingo run python check_media_files.py
```

## نکات امنیتی

⚠️ **مهم**: 
- هرگز API Secret را در کد یا repository commit نکنید
- این فایل را در `.gitignore` قرار دهید
- فقط از متغیرهای محیطی Scalingo استفاده کنید

## عیب‌یابی

### اگر فایل‌ها آپلود نمی‌شوند:

1. بررسی کنید که همه متغیرها تنظیم شده‌اند:
   ```bash
   scalingo env | grep CLOUDINARY
   ```

2. لاگ‌های اپلیکیشن را بررسی کنید:
   ```bash
   scalingo logs --lines 100
   ```

3. بررسی کنید که `django-storages` و `cloudinary` نصب شده‌اند:
   ```bash
   scalingo run pip list | grep -i cloudinary
   ```

### اگر هنوز 404 می‌بینید:

- فایل‌های قدیمی که قبل از فعال‌سازی Cloudinary آپلود شده‌اند از بین رفته‌اند
- باید آنها را دوباره آپلود کنید
- فایل‌های جدید بعد از فعال‌سازی Cloudinary به درستی کار می‌کنند

