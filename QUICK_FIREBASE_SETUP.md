# راهنمای سریع تنظیم Firebase در Scalingo

## روش سریع (توصیه می‌شود)

### 1. اجرای اسکریپت خودکار:

```powershell
# ویرایش نام اپلیکیشن در اسکریپت (خط 3)
# سپس اجرا کنید:
.\setup_firebase_auto.ps1
```

اسکریپت به صورت خودکار:
- ✅ فایل JSON را پیدا می‌کند
- ✅ به Base64 تبدیل می‌کند
- ✅ در Scalingo تنظیم می‌کند

---

## روش دستی

### مرحله 1: دریافت فایل Firebase Service Account

1. به https://console.firebase.google.com بروید
2. پروژه خود را انتخاب کنید
3. **Settings** → **Project settings** → **Service accounts**
4. روی **Generate new private key** کلیک کنید
5. فایل JSON را دانلود کنید

### مرحله 2: تبدیل به Base64

```powershell
# خواندن فایل
$json = Get-Content "service-account.json" -Raw

# تبدیل به Base64
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$base64 = [System.Convert]::ToBase64String($bytes)

# نمایش Base64 (کپی کنید)
Write-Host $base64
```

### مرحله 3: تنظیم در Scalingo

```powershell
# لاگین
scalingo login

# تنظیم (BASE64 را جایگزین کنید)
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=YOUR_BASE64_STRING"

# Restart
scalingo --app mywebsite restart
```

---

## بررسی

```powershell
# بررسی متغیرهای محیطی
scalingo --app mywebsite env | Select-String "FIREBASE"

# بررسی لاگ‌ها
scalingo --app mywebsite logs --follow
```

---

## تست

1. به `/partners/notifications/` بروید
2. یک notification تست بفرستید
3. بررسی کنید که در گوشی نمایش داده می‌شود

---

## نکات مهم

- ✅ `firebase-admin` در `requirements.txt` موجود است
- ✅ API `/api/users/fcm-token` برای ثبت token کار می‌کند
- ✅ پنل ادمین در `/partners/notifications/` برای ارسال notification است
- ✅ Token ها در مدل `Device` ذخیره می‌شوند

