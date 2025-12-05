# 🔥 راه حل نهایی برای خطای 404 FCM

## وضعیت فعلی

- ✅ Firebase Cloud Messaging API (V1) enabled است
- ✅ Role `Firebase Cloud Messaging Admin` اضافه شده (نیم ساعت پیش)
- ✅ Project ID درست است: `bonusapp-1146e`
- ✅ Service Account email درست است
- ✅ Firebase Admin SDK initialize شده
- ❌ اما هنوز خطای 404 برای `/batch`

## 🔍 علت

Service Account key که الان استفاده می‌کنید، **قبل از اضافه کردن role** generate شده است. این key permissions جدید را ندارد.

## ✅ راه حل: Generate Service Account جدید

باید Service Account جدید generate کنید که permissions کامل را داشته باشد:

### مرحله 1: Generate Service Account جدید

1. به Firebase Console بروید:
   ```
   https://console.firebase.google.com/project/bonusapp-1146e/settings/serviceaccounts/adminsdk
   ```

2. روی **"Generate new private key"** کلیک کنید

3. فایل JSON جدید را دانلود کنید

### مرحله 2: تبدیل به Base64

```powershell
$json = Get-Content "service-account.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$base64 = [System.Convert]::ToBase64String($bytes)
Write-Host $base64
```

### مرحله 3: Set در Scalingo

```powershell
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=$base64"
```

### مرحله 4: Restart

```powershell
scalingo --app mywebsite restart
```

### مرحله 5: تست

یک notification تست بفرستید و لاگ‌ها را بررسی کنید:

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG.*Firebase|ERROR|Success"
```

## ✅ انتظار

بعد از استفاده از Service Account جدید، باید ببینید:

```
✅ DEBUG: Project ID from credentials: bonusapp-1146e
✅ DEBUG: Service account email: firebase-adminsdk-...@bonusapp-1146e.iam.gserviceaccount.com
✅ DEBUG: Firebase Admin SDK initialized successfully
✅ DEBUG: Sending to X tokens via Firebase
✅ DEBUG: Firebase BatchResponse - Success: X, Failure: 0
```

**دیگر نباید ببینید:**
```
❌ HttpError 404 when requesting https://fcm.googleapis.com/batch
```

## 🎯 خلاصه

**مشکل:** Service Account key قدیمی است (قبل از اضافه کردن role)

**راه حل:** Generate Service Account جدید که permissions کامل دارد

بعد از generate کردن Service Account جدید و set کردن در Scalingo، باید کار کند.

