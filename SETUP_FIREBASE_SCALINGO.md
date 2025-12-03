# راهنمای تنظیم Firebase Credentials در Scalingo

## روش‌های تنظیم Firebase Credentials

### روش 1: استفاده از Base64 (توصیه می‌شود)

این روش ساده‌ترین و امن‌ترین روش است.

#### مرحله 1: تبدیل فایل JSON به Base64

**در Windows PowerShell:**
```powershell
# خواندن فایل و تبدیل به Base64
$jsonContent = Get-Content "path/to/service-account.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonContent)
$base64 = [System.Convert]::ToBase64String($bytes)
Write-Host $base64
```

**یا استفاده از اسکریپت:**
```powershell
.\setup_firebase_scalingo.ps1
```

#### مرحله 2: تنظیم در Scalingo

```powershell
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=YOUR_BASE64_STRING"
```

---

### روش 2: استفاده از JSON String

⚠️ **توجه**: این روش ممکن است با کاراکترهای خاص مشکل داشته باشد.

```powershell
# خواندن فایل JSON
$jsonContent = Get-Content "path/to/service-account.json" -Raw

# تنظیم در Scalingo (نیاز به escape کردن دارد)
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_JSON=$jsonContent"
```

---

### روش 3: استفاده از فایل (فقط برای local development)

این روش فقط در local development کار می‌کند. در Scalingo باید از Base64 یا JSON string استفاده کنید.

```powershell
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_FILE=/path/to/service-account.json"
```

---

## استفاده از اسکریپت خودکار

### اجرای اسکریپت:

```powershell
# ویرایش نام اپلیکیشن در اسکریپت
# سپس اجرا کنید:
.\setup_firebase_scalingo.ps1
```

اسکریپت به صورت خودکار:
1. شما را لاگین می‌کند
2. روش را می‌پرسد
3. فایل را می‌خواند و تبدیل می‌کند
4. در Scalingo تنظیم می‌کند

---

## دستورات دستی Scalingo CLI

### 1. لاگین به Scalingo:
```powershell
scalingo login
```

### 2. تبدیل فایل JSON به Base64:
```powershell
$json = Get-Content "service-account.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$base64 = [System.Convert]::ToBase64String($bytes)
```

### 3. تنظیم در Scalingo:
```powershell
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=$base64"
```

### 4. بررسی تنظیمات:
```powershell
scalingo --app mywebsite env | Select-String "FIREBASE"
```

### 5. Restart اپلیکیشن:
```powershell
scalingo --app mywebsite restart
```

---

## دریافت Firebase Service Account JSON

### مراحل:

1. به Firebase Console بروید: https://console.firebase.google.com
2. پروژه خود را انتخاب کنید
3. به **Settings** → **Project settings** بروید
4. به تب **Service accounts** بروید
5. روی **Generate new private key** کلیک کنید
6. فایل JSON را دانلود کنید

---

## بررسی تنظیمات

بعد از تنظیم، می‌توانید با دستور زیر بررسی کنید:

```powershell
scalingo --app mywebsite env | Select-String "FIREBASE"
```

باید ببینید:
```
FIREBASE_CREDENTIALS_BASE64=...
```

یا:
```
FIREBASE_CREDENTIALS_JSON=...
```

---

## تست Push Notification

بعد از تنظیم و restart:

1. به `/partners/notifications/` بروید
2. یک notification تست بفرستید
3. لاگ‌ها را بررسی کنید:
   ```powershell
   scalingo --app mywebsite logs --follow
   ```

---

## عیب‌یابی

### مشکل: Firebase Admin SDK not initialized

**راه حل:**
1. بررسی کنید که Firebase credentials درست تنظیم شده است
2. بررسی کنید که `firebase-admin` نصب شده است:
   ```bash
   pip install firebase-admin
   ```
3. اپلیکیشن را restart کنید

### مشکل: Invalid credentials

**راه حل:**
1. بررسی کنید که Base64 string کامل است
2. بررسی کنید که JSON معتبر است
3. دوباره تنظیم کنید

### مشکل: No devices found

**راه حل:**
1. مطمئن شوید که کاربران token خود را ثبت کرده‌اند
2. بررسی کنید که token در دیتابیس ذخیره شده است:
   ```python
   from notifications.models import Device
   print(Device.objects.count())
   ```

---

## نکات امنیتی

1. **هرگز** فایل service account را در git commit نکنید
2. از environment variables استفاده کنید
3. Base64 encoding امن‌تر از JSON string است
4. به صورت منظم credentials را rotate کنید

---

## خلاصه دستورات

```powershell
# 1. لاگین
scalingo login

# 2. تبدیل JSON به Base64
$json = Get-Content "service-account.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$base64 = [System.Convert]::ToBase64String($bytes)

# 3. تنظیم در Scalingo
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=$base64"

# 4. Restart
scalingo --app mywebsite restart

# 5. بررسی لاگ‌ها
scalingo --app mywebsite logs --follow
```

