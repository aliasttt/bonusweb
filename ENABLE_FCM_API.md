# 🔥 فعال کردن Firebase Cloud Messaging API

## ❌ خطای فعلی

```
firebase_admin.exceptions.NotFoundError: Unexpected HTTP response with status: 404
The requested URL /batch was not found on this server
```

## 🔍 علت

این خطا یعنی:
- ✅ Firebase Admin SDK initialize شده
- ✅ Credentials درست است
- ❌ **Firebase Cloud Messaging API (V1) فعال نیست**

## ✅ راه حل

### مرحله 1: فعال کردن FCM API در Google Cloud Console

1. **به Google Cloud Console بروید:**
   - https://console.cloud.google.com
   - پروژه Firebase خود را انتخاب کنید (`bonusapp-1146e`)

2. **API Library را باز کنید:**
   - از منوی سمت چپ: **APIs & Services** → **Library**
   - یا مستقیماً: https://console.cloud.google.com/apis/library

3. **Firebase Cloud Messaging API را پیدا کنید:**
   - در جستجو تایپ کنید: `Firebase Cloud Messaging API`
   - یا این لینک را باز کنید: https://console.cloud.google.com/apis/library/fcm.googleapis.com

4. **API را Enable کنید:**
   - روی **"Enable"** کلیک کنید
   - چند ثانیه صبر کنید تا فعال شود

### مرحله 2: بررسی Service Account Permissions

1. **به IAM & Admin بروید:**
   - https://console.cloud.google.com/iam-admin/iam
   - پروژه خود را انتخاب کنید

2. **Service Account را پیدا کنید:**
   - دنبال `firebase-adminsdk-...@bonusapp-1146e.iam.gserviceaccount.com` بگردید

3. **Permissions را بررسی کنید:**
   - باید **Firebase Cloud Messaging Admin** یا **Cloud Messaging API Service Agent** داشته باشد
   - اگر ندارد، روی **Edit** کلیک کنید و role اضافه کنید

### مرحله 3: بررسی در Firebase Console

1. **به Firebase Console بروید:**
   - https://console.firebase.google.com
   - پروژه خود را انتخاب کنید

2. **Project Settings را باز کنید:**
   - ⚙️ Settings → **Project settings**

3. **Cloud Messaging را بررسی کنید:**
   - تب **Cloud Messaging** را باز کنید
   - مطمئن شوید که Cloud Messaging فعال است

## 🔍 بررسی سریع

بعد از فعال کردن API، چند دقیقه صبر کنید (API activation ممکن است چند دقیقه طول بکشد)، سپس:

1. **Restart کنید:**
   ```powershell
   scalingo --app mywebsite restart
   ```

2. **یک notification تست بفرستید**

3. **لاگ‌ها را بررسی کنید:**
   ```powershell
   scalingo --app mywebsite logs --follow | Select-String "DEBUG|ERROR|Firebase"
   ```

## ✅ انتظار بعد از Fix

بعد از فعال کردن API، باید ببینید:

```
✅ DEBUG: Sending to X tokens via Firebase
✅ DEBUG: Firebase BatchResponse - Success: X, Failure: 0
✅ DEBUG: Token 0 (...): ✅ Success - Message ID: ...
```

**دیگر نباید ببینید:**
```
❌ NotFoundError: Unexpected HTTP response with status: 404
❌ The requested URL /batch was not found
```

## 📝 لینک‌های مفید

- **Enable FCM API:** https://console.cloud.google.com/apis/library/fcm.googleapis.com
- **IAM & Admin:** https://console.cloud.google.com/iam-admin/iam
- **Firebase Console:** https://console.firebase.google.com

## ⚠️ نکات مهم

1. **API activation ممکن است چند دقیقه طول بکشد** - صبر کنید
2. **اگر API را تازه enable کردید**، ممکن است نیاز به restart باشد
3. **Service account باید permissions درست داشته باشد**
4. **مطمئن شوید پروژه درست را انتخاب کرده‌اید** (`bonusapp-1146e`)

## 🔧 اگر هنوز کار نمی‌کند

1. **بررسی کنید API واقعاً enable شده:**
   - https://console.cloud.google.com/apis/dashboard
   - باید `Firebase Cloud Messaging API` را در لیست ببینید

2. **Service account را دوباره generate کنید:**
   - Firebase Console → Settings → Service accounts
   - Generate new private key
   - Base64 جدید را در Scalingo set کنید

3. **بررسی لاگ‌ها برای پیام‌های دقیق‌تر:**
   ```powershell
   scalingo --app mywebsite logs --follow | Select-String "ERROR|Firebase"
   ```

