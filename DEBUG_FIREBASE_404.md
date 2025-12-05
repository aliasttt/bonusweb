# 🔍 عیب‌یابی خطای 404 FCM

## ❌ خطای فعلی

```
Error sending to token ...: 404 Client Error: Not Found for url: https://fcm.googleapis.com/fcm/send
```

## 🔍 علت

این خطا یعنی:
1. ❌ Firebase Admin SDK initialize نشده
2. ❌ کد دارد fallback به Legacy FCM HTTP API می‌کند
3. ❌ Legacy API دیگر موجود نیست (404 می‌دهد)

## ✅ راه حل

### مرحله 1: بررسی لاگ‌ها برای پیام‌های DEBUG

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG"
```

**باید ببینید یکی از این پیام‌ها:**

✅ **موفق:**
```
DEBUG: Loading Firebase credentials from FIREBASE_CREDENTIALS_BASE64
DEBUG: Successfully decoded Base64 and parsed JSON
DEBUG: Firebase credentials Certificate created successfully
DEBUG: Firebase Admin SDK initialized successfully
```

❌ **خطا (یکی از این‌ها):**
```
DEBUG: Firebase credentials not found
DEBUG: Failed to decode/parse FIREBASE_CREDENTIALS_BASE64
DEBUG: Invalid Base64 encoding
DEBUG: Invalid JSON after Base64 decode
DEBUG: Failed to initialize Firebase Admin SDK
```

### مرحله 2: بررسی مقدار Base64

```powershell
# بررسی که مقدار واقعی set شده (نه placeholder)
scalingo --app mywebsite env | Select-String "FIREBASE_CREDENTIALS_BASE64"
```

**باید ببینید:**
```
FIREBASE_CREDENTIALS_BASE64=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs...  # ✅ مقدار واقعی (خیلی طولانی)
```

**نه:**
```
FIREBASE_CREDENTIALS_BASE64=<YOUR_BASE64>  # ❌ placeholder
```

### مرحله 3: بررسی مشکلات رایج

#### مشکل 1: Base64 معتبر نیست

**علائم:**
```
DEBUG: Invalid Base64 encoding
```

**راه حل:**
- دوباره فایل JSON را به Base64 تبدیل کنید
- مطمئن شوید کل Base64 را کپی کرده‌اید

#### مشکل 2: JSON معتبر نیست

**علائم:**
```
DEBUG: Invalid JSON after Base64 decode
```

**راه حل:**
- فایل `service-account.json` را بررسی کنید
- مطمئن شوید فایل کامل است

#### مشکل 3: Firebase Admin SDK نصب نیست

**علائم:**
```
DEBUG: Firebase Admin SDK not installed
```

**راه حل:**
- بررسی کنید `firebase-admin` در `requirements.txt` هست
- Scalingo را restart کنید

## 🔧 تغییرات انجام شده

1. ✅ **Fallback به Legacy API غیرفعال شد** - دیگر خطای 404 نمی‌آید
2. ✅ **لاگ‌های بیشتر اضافه شد** - حالا می‌توانید ببینید دقیقاً کجا مشکل است
3. ✅ **پیام‌های خطای واضح‌تر** - می‌گوید چرا Firebase initialize نمی‌شود

## 📝 مراحل بعدی

1. **Commit و push کنید:**
   ```powershell
   git add notifications/services.py notifications/views.py
   git commit -m "Fix: Disable Legacy FCM fallback, add better Firebase debugging"
   git push
   ```

2. **Deploy کنید** (یا Scalingo auto-deploy می‌کند)

3. **Restart:**
   ```powershell
   scalingo --app mywebsite restart
   ```

4. **بررسی لاگ‌ها:**
   ```powershell
   scalingo --app mywebsite logs --follow | Select-String "DEBUG|Firebase|ERROR"
   ```

5. **یک notification تست بفرستید** و ببینید چه پیام‌های DEBUG می‌آید

## ✅ انتظار بعد از Fix

بعد از deploy، باید ببینید:

```
✅ DEBUG: Loading Firebase credentials from FIREBASE_CREDENTIALS_BASE64
✅ DEBUG: Successfully decoded Base64 and parsed JSON
✅ DEBUG: Firebase credentials Certificate created successfully
✅ DEBUG: Firebase Admin SDK initialized successfully
✅ DEBUG: Sending to X tokens via Firebase
✅ DEBUG: Firebase BatchResponse - Success: X, Failure: 0
```

**دیگر نباید ببینید:**
```
❌ 404 Client Error: Not Found for url: https://fcm.googleapis.com/fcm/send
❌ Error sending to token ...: FCM_SERVER_KEY is not configured
```

