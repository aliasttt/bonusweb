# بررسی وضعیت Firebase

## ✅ کارهایی که انجام شد

1. ✅ `FIREBASE_CREDENTIALS_BASE64` set شد
2. ✅ اپلیکیشن restart شد

## 🔍 بررسی لاگ‌ها

برای دیدن پیام‌های Firebase، باید یک request بفرستید که Firebase را initialize کند.

### روش 1: از Dashboard

1. به `https://mybonusberlin.de/partners/notifications/` بروید
2. یک notification تست بفرستید
3. لاگ‌ها را بررسی کنید

### روش 2: از API

```powershell
# اگر token دارید:
curl -X POST https://mybonusberlin.de/api/notifications/send-test/ `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"title": "Test", "body": "Hello"}'
```

## ✅ پیام‌های موفقیت

بعد از ارسال notification، باید در لاگ‌ها ببینید:

```
✅ DEBUG: Loading Firebase credentials from FIREBASE_CREDENTIALS_BASE64
✅ DEBUG: Firebase Admin SDK initialized successfully
✅ DEBUG: Sending to X tokens via Firebase
✅ DEBUG: Firebase BatchResponse - Success: X, Failure: 0
```

## ❌ پیام‌های خطا (که دیگر نباید ببینید)

```
❌ FileNotFoundError: '/path/to/service-account.json'
❌ FCM_SERVER_KEY is not configured
❌ DEBUG: Firebase credentials not found
```

## 🔍 بررسی سریع

```powershell
# بررسی لاگ‌ها برای پیام‌های Firebase
scalingo --app mywebsite logs --follow | Select-String "DEBUG|Firebase|FCM"
```

یا فقط منتظر بمانید تا یک notification واقعی ارسال شود.

