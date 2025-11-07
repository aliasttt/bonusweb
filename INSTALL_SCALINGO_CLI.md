# راهنمای نصب Scalingo CLI و اجرای Migration

## روش 1: دانلود مستقیم (توصیه می‌شود)

### مرحله 1: دانلود Scalingo CLI

1. به آدرس زیر بروید:
   ```
   https://cli.scalingo.com/install
   ```

2. یا مستقیماً از GitHub دانلود کنید:
   ```
   https://github.com/Scalingo/cli/releases/latest/download/scalingo_windows_amd64.exe
   ```

3. فایل `scalingo_windows_amd64.exe` را دانلود کنید

### مرحله 2: نصب

1. فایل دانلود شده را اجرا کنید
2. فایل را در یک مسیر مناسب قرار دهید (مثلاً `C:\Program Files\Scalingo\`)
3. مسیر را به PATH اضافه کنید:
   - Windows Settings → System → About → Advanced system settings
   - Environment Variables → System variables → Path → Edit
   - New → مسیر نصب را اضافه کنید

### مرحله 3: لاگین

PowerShell را باز کنید و دستور زیر را اجرا کنید:

```powershell
scalingo login
```

این دستور مرورگر را باز می‌کند و از شما می‌خواهد که لاگین کنید.

### مرحله 4: اجرای Migration

بعد از لاگین، دستور زیر را اجرا کنید:

```powershell
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## روش 2: استفاده از Chocolatey (اگر نصب دارید)

```powershell
# نصب Scalingo CLI
choco install scalingo-cli -y

# لاگین
scalingo login

# اجرای migration
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## روش 3: استفاده از Dashboard Scalingo (بدون نصب CLI)

1. به آدرس زیر بروید:
   ```
   https://dashboard.scalingo.com
   ```

2. اپلیکیشن `mywebsite` را انتخاب کنید

3. به بخش **"One-off containers"** یا **"Run command"** بروید

4. دستور زیر را وارد کنید:
   ```
   python manage.py migrate accounts
   ```

5. روی **"Run"** کلیک کنید

---

## دستورات مفید بعد از نصب

```powershell
# بررسی نسخه
scalingo --version

# لاگین
scalingo login

# بررسی لاگین بودن
scalingo whoami

# بررسی وضعیت migration ها
scalingo --app mywebsite run python manage.py showmigrations accounts

# اجرای migration
scalingo --app mywebsite run python manage.py migrate accounts

# اجرای همه migration ها
scalingo --app mywebsite run python manage.py migrate

# مشاهده لاگ‌ها
scalingo --app mywebsite logs

# مشاهده لاگ‌های real-time
scalingo --app mywebsite logs --follow
```

---

## عیب‌یابی

### مشکل: "scalingo is not recognized"

**راه حل:**
- مطمئن شوید که Scalingo CLI نصب شده است
- مسیر نصب را به PATH اضافه کنید
- PowerShell را restart کنید

### مشکل: "You are not logged in"

**راه حل:**
```powershell
scalingo login
```

### مشکل: "App not found"

**راه حل:**
- مطمئن شوید که نام اپلیکیشن درست است: `mywebsite`
- اگر نام متفاوت است، در دستورات `mywebsite` را با نام واقعی جایگزین کنید

---

## نکات مهم

1. **بکاپ بگیرید**: قبل از اجرای migration، حتماً از دیتابیس بکاپ بگیرید
2. **زمان مناسب**: migration را در ساعات کم‌ترافیک اجرا کنید
3. **بررسی لاگ**: بعد از اجرا، لاگ‌ها را بررسی کنید
4. **تست**: بعد از migration، API را تست کنید

---

## خلاصه سریع

```powershell
# 1. نصب Scalingo CLI (از https://cli.scalingo.com/install)
# 2. لاگین
scalingo login

# 3. اجرای migration
scalingo --app mywebsite run python manage.py migrate accounts
```

