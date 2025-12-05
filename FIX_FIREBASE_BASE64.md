# 🔥 رفع مشکل Firebase - استفاده از Base64

## مشکل اصلی

خطای `FileNotFoundError: '/path/to/service-account.json'` به این دلیل بود که:

1. ❌ کد اول `FIREBASE_CREDENTIALS_FILE` را چک می‌کرد (که placeholder بود)
2. ❌ بعد از آن `FIREBASE_CREDENTIALS_BASE64` را چک می‌کرد
3. ❌ چون `FIREBASE_CREDENTIALS_FILE` وجود داشت (حتی placeholder)، کد سعی می‌کرد فایل را باز کند

## راه حل

### تغییر اولویت در `notifications/services.py`

**قبل:**
```python
Priority:
1. FIREBASE_CREDENTIALS_FILE  # ❌ اول این چک می‌شد
2. FIREBASE_CREDENTIALS_JSON
3. FIREBASE_CREDENTIALS_BASE64  # ✅ این آخر بود
```

**بعد:**
```python
Priority:
1. FIREBASE_CREDENTIALS_BASE64  # ✅ اول این چک می‌شود (توصیه شده)
2. FIREBASE_CREDENTIALS_JSON
3. FIREBASE_CREDENTIALS_FILE  # فقط اگر فایل واقعی وجود داشته باشد
```

## تغییرات انجام شده

### 1. اولویت Base64
- حالا `FIREBASE_CREDENTIALS_BASE64` اول چک می‌شود
- اگر set باشد، فوراً استفاده می‌شود
- دیگر به `FIREBASE_CREDENTIALS_FILE` نگاه نمی‌کند

### 2. Skip کردن Placeholder
- اگر `FIREBASE_CREDENTIALS_FILE` برابر `/path/to/service-account.json` باشد، کاملاً skip می‌شود
- هیچ تلاشی برای باز کردن فایل نمی‌کند

### 3. پیام‌های خطای بهتر
- اگر Legacy API نیاز باشد، پیام واضح می‌دهد که در پروژه‌های جدید (2024+) دیگر موجود نیست

## نتیجه

✅ حالا کد:
1. اول `FIREBASE_CREDENTIALS_BASE64` را چک می‌کند
2. اگر set باشد، فوراً استفاده می‌کند
3. دیگر خطای `FileNotFoundError` نمی‌دهد
4. Firebase Admin SDK درست initialize می‌شود
5. نیازی به `FCM_SERVER_KEY` نیست (چون Legacy API غیرفعال است)

## مراحل بعدی

1. ✅ کد اصلاح شد
2. ⏳ باید commit و push کنید
3. ⏳ Scalingo باید redeploy شود
4. ✅ `FIREBASE_CREDENTIALS_BASE64` را در Scalingo set کنید (اگر هنوز نکرده‌اید)
5. ✅ `FIREBASE_CREDENTIALS_FILE` را unset کنید (اگر set است)

## دستورات Scalingo

```powershell
# حذف placeholder (اگر وجود دارد)
scalingo --app mywebsite env-unset FIREBASE_CREDENTIALS_FILE

# بررسی که Base64 set است
scalingo --app mywebsite env | Select-String "FIREBASE_CREDENTIALS_BASE64"

# Restart
scalingo --app mywebsite restart

# بررسی لاگ‌ها
scalingo --app mywebsite logs --follow
```

## انتظار در لاگ‌ها

بعد از deploy، باید ببینید:

```
DEBUG: Loading Firebase credentials from FIREBASE_CREDENTIALS_BASE64
DEBUG: Firebase Admin SDK initialized successfully
```

و دیگر نباید ببینید:
```
❌ FileNotFoundError: '/path/to/service-account.json'
❌ FCM_SERVER_KEY is not configured
```

