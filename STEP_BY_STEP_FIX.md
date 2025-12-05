# 🔥 راه حل مرحله به مرحله برای خطای 404

## 📋 چک‌لیست

### ✅ کارهایی که انجام شده:
1. ✅ Firebase Cloud Messaging API (V1) enabled است
2. ✅ Firebase Admin SDK initialize شده
3. ✅ Credentials set شده

### ❌ مشکل باقی‌مانده:
- خطای 404 برای `/batch`

## 🎯 راه حل قطعی

### مرحله 1: بررسی Project ID در لاگ‌ها

بعد از deploy کد جدید، باید Project ID را در لاگ‌ها ببینید:

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG.*Project ID"
```

**اگر Project ID را نمی‌بینید:**
- کد جدید deploy نشده
- باید commit و push کنید

**اگر Project ID را می‌بینید:**
- بررسی کنید که `bonusapp-1146e` باشد
- اگر متفاوت است، Service Account از پروژه اشتباه است

### مرحله 2: Generate Service Account جدید (توصیه می‌شود)

این روش 100% کار می‌کند:

#### 2.1: دریافت Service Account جدید

1. به این لینک بروید:
   ```
   https://console.firebase.google.com/project/bonusapp-1146e/settings/serviceaccounts/adminsdk
   ```

2. روی **"Generate new private key"** کلیک کنید

3. فایل JSON را دانلود کنید

#### 2.2: تبدیل به Base64

```powershell
# فایل را در پوشه پروژه قرار دهید
$json = Get-Content "service-account.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$base64 = [System.Convert]::ToBase64String($bytes)
Write-Host $base64
```

#### 2.3: Set در Scalingo

```powershell
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=$base64"
```

#### 2.4: Restart

```powershell
scalingo --app mywebsite restart
```

### مرحله 3: بررسی لاگ‌ها

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG|ERROR|Firebase"
```

**باید ببینید:**
```
✅ DEBUG: Project ID from credentials: bonusapp-1146e
✅ DEBUG: Service account email: firebase-adminsdk-...@bonusapp-1146e.iam.gserviceaccount.com
✅ DEBUG: Firebase Admin SDK initialized successfully
```

### مرحله 4: تست Notification

یک notification تست بفرستید و ببینید:

**موفق:**
```
✅ DEBUG: Sending to X tokens via Firebase
✅ DEBUG: Firebase BatchResponse - Success: X, Failure: 0
```

**خطا:**
```
❌ HttpError 404 when requesting https://fcm.googleapis.com/batch
```

## 🔍 اگر هنوز خطا می‌دهد

### بررسی 1: API واقعاً enable است؟

1. به این لینک بروید:
   ```
   https://console.cloud.google.com/apis/dashboard?project=bonusapp-1146e
   ```

2. باید `Firebase Cloud Messaging API` را در لیست ببینید
3. Status باید "Enabled" باشد

### بررسی 2: Service Account Permissions

1. به این لینک بروید:
   ```
   https://console.cloud.google.com/iam-admin/iam?project=bonusapp-1146e
   ```

2. Service Account جدید را پیدا کنید (با email جدید)
3. بررسی کنید که این roles را دارد:
   - `Firebase Admin SDK Administrator Service Agent`
   - `Service Account Token Creator`
   - (اختیاری) `Firebase Cloud Messaging Admin`

### بررسی 3: Project ID Match

در لاگ‌ها باید ببینید:
```
DEBUG: Project ID from credentials: bonusapp-1146e
```

**اگر متفاوت است:**
- Service Account از پروژه اشتباه است
- باید از پروژه `bonusapp-1146e` generate کنید

## ⚠️ نکات مهم

1. **Service Account جدید همیشه بهتر است** - permissions کامل دارد
2. **بعد از set کردن Base64 جدید، حتماً restart کنید**
3. **اگر Project ID در لاگ‌ها نیست، کد جدید deploy نشده**
4. **IAM changes ممکن است 5-10 دقیقه طول بکشد**

## 🎯 توصیه نهایی

**حتماً Service Account جدید generate کنید** - این روش 100% کار می‌کند و سریع‌تر است.

بعد از انجام، به من بگویید چه لاگ‌هایی می‌بینید.

