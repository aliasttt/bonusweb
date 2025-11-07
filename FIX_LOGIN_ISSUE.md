# حل مشکل لاگین Scalingo

## مشکل: "unauthorized - you are not authorized to do this operation"

این خطا یعنی:
- Username یا Password اشتباه است
- یا اکانت Scalingo مشکل دارد

---

## راه حل 1: استفاده از API Token (توصیه می‌شود)

### مرحله 1: ایجاد API Token

1. به Dashboard Scalingo بروید:
   ```
   https://dashboard.scalingo.com
   ```

2. لاگین کنید با:
   - Email: `aliasadi3853@gmail.com`
   - Password: `Aasadi2233#`

3. به بخش **"Account"** → **"API Tokens"** بروید:
   ```
   https://dashboard.scalingo.com/account/tokens
   ```

4. روی **"Create a new token"** کلیک کنید

5. یک نام برای token بدهید (مثلاً: `migration-token`)

6. Token را کپی کنید (فقط یک بار نمایش داده می‌شود!)

### مرحله 2: لاگین با API Token

```powershell
# اضافه کردن به PATH (اگر قبلاً نکرده‌اید)
$env:Path += ";$env:USERPROFILE\AppData\Local\Programs\Scalingo"

# لاگین با API Token
scalingo login --api-token
```

بعد از اجرا، API Token را paste کنید.

---

## راه حل 2: بررسی Username/Password

مطمئن شوید که:
- Username: `aliasttt` یا `aliasadi3853@gmail.com`
- Password: `Aasadi2233#`

دوباره امتحان کنید:
```powershell
scalingo login
```

---

## راه حل 3: استفاده از Dashboard (بدون CLI)

اگر لاگین با CLI مشکل دارد، از Dashboard استفاده کنید:

1. به https://dashboard.scalingo.com بروید
2. لاگین کنید
3. اپلیکیشن `mywebsite` را انتخاب کنید
4. به بخش **"One-off containers"** بروید
5. دستور زیر را وارد کنید:
   ```
   python manage.py migrate accounts
   ```
6. روی **"Run"** کلیک کنید

---

## راه حل 4: Reset Password

اگر password را فراموش کرده‌اید:

1. به https://dashboard.scalingo.com بروید
2. روی **"Forgot password?"** کلیک کنید
3. Email خود را وارد کنید: `aliasadi3853@gmail.com`
4. لینک reset password را از ایمیل دریافت کنید
5. Password جدید تنظیم کنید

---

## دستورات مفید

```powershell
# اضافه کردن به PATH
$env:Path += ";$env:USERPROFILE\AppData\Local\Programs\Scalingo"

# بررسی لاگین بودن
scalingo whoami

# لاگین با API Token
scalingo login --api-token

# لاگین عادی
scalingo login

# اجرای Migration (بعد از لاگین)
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## توصیه

**بهترین روش:** استفاده از API Token (راه حل 1)

این روش:
- امن‌تر است
- نیاز به password ندارد
- برای automation بهتر است

