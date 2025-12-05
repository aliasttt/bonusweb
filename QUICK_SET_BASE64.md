# 🚀 راهنمای سریع: تنظیم FIREBASE_CREDENTIALS_BASE64

## ⚠️ مشکل فعلی

مقدار فعلی در Scalingo:
```
FIREBASE_CREDENTIALS_BASE64=<YOUR_BASE64>
```

این یک **placeholder** است، نه مقدار واقعی! باید با Base64 واقعی جایگزین شود.

## ✅ راه حل سریع

### روش 1: استفاده از اسکریپت (توصیه می‌شود)

```powershell
.\SET_FIREBASE_BASE64.ps1
```

اسکریپت به صورت خودکار:
- فایل `service-account.json` را پیدا می‌کند
- به Base64 تبدیل می‌کند
- در Scalingo set می‌کند

### روش 2: دستی

#### مرحله 1: دریافت فایل Service Account

1. به https://console.firebase.google.com بروید
2. پروژه خود را انتخاب کنید
3. **Settings** → **Project settings** → **Service accounts**
4. روی **"Generate new private key"** کلیک کنید
5. فایل JSON را دانلود کنید (مثلاً `bonusapp-1146e-firebase-adminsdk-xxxxx.json`)

#### مرحله 2: تبدیل به Base64

```powershell
# فایل را در پوشه پروژه قرار دهید
# سپس اجرا کنید:

$json = Get-Content "service-account.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$base64 = [System.Convert]::ToBase64String($bytes)
Write-Host $base64
```

#### مرحله 3: Set در Scalingo

```powershell
# Base64 را کپی کنید و جایگزین کنید:
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=<PASTE_BASE64_HERE>"
```

**مثال:**
```powershell
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6..."
```

## ✅ بررسی

```powershell
# بررسی که مقدار واقعی set شده (نه placeholder):
scalingo --app mywebsite env | Select-String "FIREBASE_CREDENTIALS_BASE64"
```

**باید ببینید:**
```
FIREBASE_CREDENTIALS_BASE64=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6...  # ✅ مقدار واقعی
```

**نه:**
```
FIREBASE_CREDENTIALS_BASE64=<YOUR_BASE64>  # ❌ placeholder
```

## 🔄 Restart و بررسی

```powershell
# Restart
scalingo --app mywebsite restart

# بررسی لاگ‌ها
scalingo --app mywebsite logs --follow
```

**باید ببینید:**
```
✅ DEBUG: Loading Firebase credentials from FIREBASE_CREDENTIALS_BASE64
✅ DEBUG: Firebase Admin SDK initialized successfully
```

**دیگر نباید ببینید:**
```
❌ FileNotFoundError: '/path/to/service-account.json'
❌ FCM_SERVER_KEY is not configured
```

## 📝 نکات مهم

1. **فایل JSON را commit نکنید** (در `.gitignore` است)
2. **Base64 می‌تواند خیلی طولانی باشد** (چند هزار کاراکتر) - این طبیعی است
3. **اگر Base64 خیلی کوتاه است** (مثلاً 50 کاراکتر)، احتمالاً اشتباه است
4. **Base64 واقعی معمولاً با `eyJ` شروع می‌شود** (base64 برای `{"`)

## 🔍 عیب‌یابی

### اگر Base64 set نشد:

```powershell
# بررسی مقدار فعلی
scalingo --app mywebsite env | Select-String "FIREBASE_CREDENTIALS_BASE64"

# اگر هنوز placeholder است، دوباره set کنید
```

### اگر خطای "Invalid base64" می‌دهد:

- مطمئن شوید کل Base64 را کپی کرده‌اید (می‌تواند چند خط باشد)
- مطمئن شوید فایل JSON معتبر است
- دوباره تبدیل کنید

### اگر هنوز خطا می‌دهد:

```powershell
# بررسی لاگ‌ها برای پیام‌های DEBUG
scalingo --app mywebsite logs --follow | Select-String "DEBUG"
```

