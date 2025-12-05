# 🔥 راه حل نهایی برای خطای 404 FCM

## ❌ مشکل فعلی

```
HttpError 404 when requesting https://fcm.googleapis.com/batch returned "Not Found"
```

## ✅ چک‌لیست کامل

### 1. ✅ API Enabled است
- Firebase Cloud Messaging API (V1) در Firebase Console enabled است

### 2. ⚠️ Service Account Role
- باید `Firebase Cloud Messaging Admin` role داشته باشد
- اگر اضافه کردید، **5-10 دقیقه صبر کنید** تا propagate شود

### 3. 🔍 بررسی Project ID

بعد از deploy کد جدید، در لاگ‌ها باید ببینید:

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG.*Project ID"
```

**باید ببینید:**
```
DEBUG: Project ID from credentials: bonusapp-1146e
```

**اگر Project ID متفاوت است:**
- Service Account از پروژه اشتباه است
- باید Service Account جدید از پروژه درست generate کنید

### 4. 🔄 Generate Service Account جدید

اگر role اضافه کردید و هنوز کار نمی‌کند، Service Account جدید generate کنید:

1. **Firebase Console:**
   - https://console.firebase.google.com/project/bonusapp-1146e/settings/serviceaccounts/adminsdk

2. **Generate new private key**

3. **فایل جدید را به Base64 تبدیل کنید:**
   ```powershell
   $json = Get-Content "service-account.json" -Raw
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
   $base64 = [System.Convert]::ToBase64String($bytes)
   Write-Host $base64
   ```

4. **در Scalingo set کنید:**
   ```powershell
   scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=$base64"
   ```

5. **Restart:**
   ```powershell
   scalingo --app mywebsite restart
   ```

### 5. 🔍 بررسی دقیق‌تر

بعد از deploy کد جدید، این لاگ‌ها را بررسی کنید:

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG.*Project|DEBUG.*Service account|ERROR"
```

**باید ببینید:**
```
DEBUG: Project ID from credentials: bonusapp-1146e
DEBUG: Service account email: firebase-adminsdk-...@bonusapp-1146e.iam.gserviceaccount.com
```

## 🎯 راه حل پیشنهادی (مرحله به مرحله)

### مرحله 1: بررسی Role (اگر هنوز اضافه نکردید)

1. به https://console.cloud.google.com/iam-admin/iam بروید
2. Service Account `firebase-adminsdk-fbsvc@bonusapp-1146e.iam.gserviceaccount.com` را پیدا کنید
3. Edit → Add Another Role → `Firebase Cloud Messaging Admin`
4. Save
5. **10 دقیقه صبر کنید**

### مرحله 2: Generate Service Account جدید (توصیه می‌شود)

1. Firebase Console → Settings → Service accounts
2. Generate new private key
3. فایل را به Base64 تبدیل کنید
4. در Scalingo set کنید
5. Restart کنید

### مرحله 3: بررسی لاگ‌ها

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG|ERROR|Firebase"
```

**باید ببینید:**
```
✅ DEBUG: Project ID from credentials: bonusapp-1146e
✅ DEBUG: Firebase Admin SDK initialized successfully
✅ DEBUG: Sending to X tokens via Firebase
✅ DEBUG: Firebase BatchResponse - Success: X, Failure: 0
```

## ⚠️ نکات مهم

1. **IAM changes ممکن است 5-10 دقیقه طول بکشد** - صبر کنید
2. **Service Account جدید همیشه بهتر است** - permissions کامل دارد
3. **Project ID باید دقیقاً `bonusapp-1146e` باشد**
4. **بعد از هر تغییر، restart کنید**

## 🔧 اگر هنوز کار نمی‌کند

1. **بررسی کنید API واقعاً enable است:**
   - https://console.cloud.google.com/apis/dashboard?project=bonusapp-1146e
   - باید `Firebase Cloud Messaging API` را ببینید

2. **بررسی کنید Service Account درست است:**
   - Project ID در credentials = `bonusapp-1146e`
   - Client email شامل `bonusapp-1146e` باشد

3. **لاگ‌های کامل را بررسی کنید:**
   ```powershell
   scalingo --app mywebsite logs --follow > logs.txt
   # سپس logs.txt را بررسی کنید
   ```

