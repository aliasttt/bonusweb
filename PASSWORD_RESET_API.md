## فراموشی رمز عبور (OTP ایمیل)

Base URL:
- Development: `http://127.0.0.1:8000`
- Production: `https://<your-domain>`

Prefix های رایج:
- بدون ورژن: `/api/accounts/...`
- با ورژن v1 (در صورت نیاز): `/api/v1/accounts/...` (اگر همین فایل را همان مسیر اضافه کردید، از همین route هم کار می‌کند)

---

### 1) ارسال کد به ایمیل
POST `/api/accounts/password/forgot/`

Body:
```json
{
  "email": "user@example.com"
}
```

Response (همیشه 200 – جلوگیری از enum ایمیل):
```json
{ "message": "If the email exists, a reset code has been sent." }
```

نکات:
- کد 6 رقمی تولید و برای 10 دقیقه اعتبار دارد.
- ایمیل اگر در سیستم نباشد باز هم پاسخ 200 داده می‌شود.

---

### 2) اعتبارسنجی کد
POST `/api/accounts/password/verify/`

Body:
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

Responses:
- 200:
```json
{ "valid": true }
```
- 400: `{"detail": "invalid code"}` یا `{"detail": "code expired"}`

---

### 3) تنظیم رمز جدید
POST `/api/accounts/password/reset/`

Body:
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "NewStrongPass123!",
  "confirm_password": "NewStrongPass123!"
}
```

Responses:
- 200:
```json
{ "message": "password reset successful" }
```
- 400: `invalid code or email`، `code expired`، یا `passwords do not match`

رمز با `set_password` هش می‌شود و تمام کدهای فعال کاربر مصرف می‌گردند.

---

### نمونه‌های curl

ارسال کد:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/password/forgot/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

اعتبارسنجی کد:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/password/verify/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'
```

ریست رمز:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456", "new_password": "NewStrongPass123!", "confirm_password": "NewStrongPass123!"}'
```

---

### تنظیمات ایمیل (اختیاری)
برای ارسال واقعی ایمیل، در `settings.py` تنظیمات SMTP را قرار دهید. در توسعه اگر تنظیم نشده باشد ممکن است ارسال واقعی انجام نشود.

نمونه (SMTP جیمیل – برای تست‌های موقت):
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your@gmail.com"
EMAIL_HOST_PASSWORD = "app-password"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

در تولید از سرویس‌های ایمیل معتبر استفاده کنید.




