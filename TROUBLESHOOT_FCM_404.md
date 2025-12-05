# 🔍 عیب‌یابی کامل خطای 404 FCM

## وضعیت فعلی

- ✅ Firebase Cloud Messaging API (V1) enabled در Firebase Console
- ✅ Role `Firebase Cloud Messaging Admin` اضافه شده
- ✅ Service Account جدید generate شده
- ✅ Project ID درست است: `bonusapp-1146e`
- ✅ Firebase Admin SDK initialize شده
- ❌ اما هنوز خطای 404 برای `/batch`

## 🔍 بررسی‌های لازم

### 1. بررسی API در Google Cloud Console (نه Firebase Console)

API باید در **Google Cloud Console** enable باشد، نه فقط Firebase Console.

1. به Google Cloud Console بروید:
   ```
   https://console.cloud.google.com/apis/dashboard?project=bonusapp-1146e
   ```

2. در جستجو تایپ کنید: `Firebase Cloud Messaging API`

3. بررسی کنید که:
   - API در لیست باشد
   - Status = **"Enabled"** باشد

4. اگر **"Disabled"** است:
   - روی API کلیک کنید
   - **"Enable"** را بزنید
   - چند دقیقه صبر کنید

### 2. بررسی Billing

بعضی API‌ها نیاز به billing فعال دارند:

1. به Google Cloud Console بروید:
   ```
   https://console.cloud.google.com/billing?project=bonusapp-1146e
   ```

2. بررسی کنید که billing account linked باشد

### 3. بررسی API در Firebase Console

1. به Firebase Console بروید:
   ```
   https://console.firebase.google.com/project/bonusapp-1146e/settings/cloudmessaging
   ```

2. بررسی کنید که:
   - "Firebase Cloud Messaging API (V1)" = **Enabled** ✅
   - "Cloud Messaging API (Legacy)" = Disabled (این درست است)

### 4. بررسی Service Account Permissions (دوباره)

1. به Google Cloud Console بروید:
   ```
   https://console.cloud.google.com/iam-admin/iam?project=bonusapp-1146e
   ```

2. Service Account `firebase-adminsdk-fbsvc@bonusapp-1146e.iam.gserviceaccount.com` را پیدا کنید

3. بررسی کنید که این roles را دارد:
   - ✅ `Firebase Admin SDK Administrator Service Agent`
   - ✅ `Firebase Cloud Messaging Admin`
   - ✅ `Service Account Token Creator`

### 5. بررسی Project ID Match

در لاگ‌ها باید ببینید:
```
DEBUG: Project ID from credentials: bonusapp-1146e
```

**اگر متفاوت است:**
- Service Account از پروژه اشتباه است
- باید از پروژه `bonusapp-1146e` generate کنید

## 🔧 راه حل‌های پیشنهادی

### راه حل 1: Enable API در Google Cloud Console

```
https://console.cloud.google.com/apis/library/fcm.googleapis.com?project=bonusapp-1146e
```

- روی **"Enable"** کلیک کنید
- چند دقیقه صبر کنید
- Restart کنید

### راه حل 2: بررسی Billing

اگر billing فعال نیست، فعال کنید.

### راه حل 3: بررسی دقیق‌تر لاگ‌ها

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG|ERROR|Firebase|FCM|batch"
```

ببینید آیا پیام خاصی هست که نشان دهد مشکل کجاست.

## ⚠️ نکات مهم

1. **API باید در Google Cloud Console enable باشد** (نه فقط Firebase Console)
2. **IAM changes ممکن است 10-15 دقیقه طول بکشد**
3. **بعد از enable کردن API، چند دقیقه صبر کنید**
4. **Restart کنید بعد از هر تغییر**

## 🎯 احتمال قوی

**API در Google Cloud Console enable نیست.**

حتماً بررسی کنید:
```
https://console.cloud.google.com/apis/dashboard?project=bonusapp-1146e
```

باید `Firebase Cloud Messaging API` را ببینید و Status = "Enabled" باشد.

