# دستورات لاگین Scalingo

## روش 1: لاگین با API Token

### مرحله 1: دریافت API Token

1. به https://dashboard.scalingo.com بروید
2. لاگین کنید
3. به بخش **"Account"** → **"API Tokens"** بروید:
   ```
   https://dashboard.scalingo.com/account/tokens
   ```
4. روی **"Create a new token"** کلیک کنید
5. یک نام بدهید (مثلاً: `migration-token`)
6. Token را کپی کنید

### مرحله 2: لاگین با Token

**روش A: بدون argument (interactive):**
```powershell
scalingo login --api-token
```
بعد از اجرا، token را paste کنید.

**روش B: با token در دستور (اگر syntax پشتیبانی کند):**
```powershell
scalingo login --api-token YOUR_TOKEN_HERE
```

---

## روش 2: لاگین عادی (Username/Password)

```powershell
scalingo login
```

بعد از اجرا:
- Username: `aliasttt` یا `aliasadi3853@gmail.com`
- Password: `Aasadi2233#`

---

## روش 3: استفاده از Dashboard (بدون CLI)

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

## بررسی لاگین بودن

```powershell
scalingo whoami
```

---

## اجرای Migration (بعد از لاگین)

```powershell
scalingo --app mywebsite run python manage.py migrate accounts
```

