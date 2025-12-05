# 🔍 عیب‌یابی خطای 404 با FCM API Enabled

## ✅ وضعیت فعلی

- ✅ Firebase Cloud Messaging API (V1) **Enabled** است
- ✅ Firebase Admin SDK initialize شده
- ✅ Credentials set شده
- ❌ اما هنوز خطای 404 برای `/batch` می‌آید

## 🔍 علل احتمالی

### 1. Service Account Permissions

Service account ممکن است permissions لازم را نداشته باشد.

**بررسی:**
1. به https://console.cloud.google.com/iam-admin/iam بروید
2. پروژه `bonusapp-1146e` را انتخاب کنید
3. Service account `firebase-adminsdk-...@bonusapp-1146e.iam.gserviceaccount.com` را پیدا کنید
4. بررسی کنید که این roles را دارد:
   - `Firebase Cloud Messaging Admin`
   - یا `Cloud Messaging API Service Agent`

**اگر ندارد:**
- روی **Edit** کلیک کنید
- **Add Another Role** → `Firebase Cloud Messaging Admin` را اضافه کنید

### 2. Project ID Mismatch

Project ID در credentials ممکن است با پروژه Firebase match نکند.

**بررسی:**
```powershell
# بررسی Project ID در credentials
$json = Get-Content "service-account.json" -Raw | ConvertFrom-Json
Write-Host "Project ID in credentials: $($json.project_id)"
```

**باید باشد:** `bonusapp-1146e`

**اگر نیست:**
- Service account جدید از پروژه درست generate کنید
- Base64 جدید را در Scalingo set کنید

### 3. Firebase Admin SDK Version

Version قدیمی Firebase Admin SDK ممکن است مشکل داشته باشد.

**بررسی:**
```powershell
# در Scalingo یا local
pip show firebase-admin
```

**باید:** Version 6.0.0 یا جدیدتر

**اگر قدیمی است:**
- در `requirements.txt` بررسی کنید
- Scalingo را restart کنید

### 4. Service Account Key قدیمی

Service account key ممکن است منقضی شده یا invalid باشد.

**راه حل:**
1. به Firebase Console بروید
2. Settings → Service accounts
3. **Generate new private key**
4. فایل جدید را به Base64 تبدیل کنید
5. در Scalingo set کنید

## 🔧 راه حل‌های پیشنهادی

### راه حل 1: بررسی Service Account Permissions

```powershell
# 1. به Google Cloud Console بروید
# https://console.cloud.google.com/iam-admin/iam

# 2. Service account را پیدا کنید
# 3. Roles را بررسی کنید
# 4. اگر لازم است، Firebase Cloud Messaging Admin را اضافه کنید
```

### راه حل 2: Generate Service Account جدید

```powershell
# 1. به Firebase Console بروید
# https://console.firebase.google.com/project/bonusapp-1146e/settings/serviceaccounts/adminsdk

# 2. Generate new private key
# 3. فایل را دانلود کنید
# 4. به Base64 تبدیل کنید:
$json = Get-Content "service-account.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$base64 = [System.Convert]::ToBase64String($bytes)

# 5. در Scalingo set کنید:
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=$base64"

# 6. Restart:
scalingo --app mywebsite restart
```

### راه حل 3: بررسی Project ID

```powershell
# بررسی Project ID در credentials
$json = Get-Content "service-account.json" -Raw | ConvertFrom-Json
Write-Host "Project ID: $($json.project_id)"
Write-Host "Client Email: $($json.client_email)"

# باید project_id = "bonusapp-1146e" باشد
```

## 📝 بررسی دقیق‌تر

بعد از اعمال تغییرات، لاگ‌ها را بررسی کنید:

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG|ERROR|Firebase|FCM"
```

**باید ببینید:**
```
✅ DEBUG: Loading Firebase credentials from FIREBASE_CREDENTIALS_BASE64
✅ DEBUG: Firebase Admin SDK initialized successfully
✅ DEBUG: Sending to X tokens via Firebase
```

**اگر هنوز خطا می‌بینید:**
- پیام خطای کامل را کپی کنید
- بررسی کنید که دقیقاً چه خطایی می‌دهد

## 🎯 احتمال قوی: Service Account Permissions

با توجه به اینکه API enabled است اما 404 می‌دهد، **احتمال قوی این است که Service Account permissions ندارد**.

حتماً بررسی کنید:
1. Service account در Google Cloud Console
2. Roles و Permissions
3. اگر لازم است، `Firebase Cloud Messaging Admin` role را اضافه کنید

