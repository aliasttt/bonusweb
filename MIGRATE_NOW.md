# 🚀 راهنمای سریع اجرای Migration در Scalingo

## ⚡ روش 1: Dashboard Scalingo (سریع‌ترین - بدون نصب)

### مراحل:

1. **باز کردن Dashboard:**
   - به آدرس زیر بروید: https://dashboard.scalingo.com
   - لاگین کنید

2. **انتخاب اپلیکیشن:**
   - اپلیکیشن `mywebsite` را انتخاب کنید

3. **اجرای Migration:**
   - به بخش **"One-off containers"** یا **"Run command"** بروید
   - دستور زیر را وارد کنید:
     ```
     python manage.py migrate accounts
     ```
   - روی **"Run"** کلیک کنید

4. **بررسی نتیجه:**
   - منتظر بمانید تا migration اجرا شود
   - لاگ‌ها را بررسی کنید

✅ **تمام!** Migration اجرا می‌شود.

---

## 🔧 روش 2: CLI (برای استفاده مداوم)

### مرحله 1: دانلود Scalingo CLI

**لینک مستقیم دانلود:**
```
https://github.com/Scalingo/cli/releases/latest/download/scalingo_windows_amd64.exe
```

یا:
```
https://cli.scalingo.com/install
```

### مرحله 2: نصب

1. فایل `scalingo_windows_amd64.exe` را دانلود کنید
2. فایل را در یک مسیر مناسب قرار دهید (مثلاً `C:\Program Files\Scalingo\`)
3. مسیر را به PATH اضافه کنید:
   - Windows Settings → System → About → Advanced system settings
   - Environment Variables → User variables → Path → Edit
   - New → مسیر نصب را اضافه کنید (مثلاً `C:\Program Files\Scalingo`)

### مرحله 3: اجرای دستورات

PowerShell را باز کنید و دستورات زیر را اجرا کنید:

```powershell
# لاگین (اولین بار)
scalingo login

# بررسی وضعیت migration ها
scalingo --app mywebsite run python manage.py showmigrations accounts

# اجرای migration
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## 📝 دستورات مفید

```powershell
# بررسی نسخه CLI
scalingo --version

# لاگین
scalingo login

# بررسی لاگین بودن
scalingo whoami

# بررسی وضعیت migration ها
scalingo --app mywebsite run python manage.py showmigrations accounts

# اجرای migration خاص
scalingo --app mywebsite run python manage.py migrate accounts

# اجرای همه migration ها
scalingo --app mywebsite run python manage.py migrate

# مشاهده لاگ‌ها
scalingo --app mywebsite logs

# مشاهده لاگ‌های real-time
scalingo --app mywebsite logs --follow
```

---

## ✅ بررسی نتیجه

بعد از اجرای migration، می‌توانید با دستور زیر بررسی کنید:

```powershell
scalingo --app mywebsite run python manage.py showmigrations accounts
```

باید همه migration ها با `[X]` علامت‌گذاری شده باشند.

---

## 🆘 عیب‌یابی

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

## 📌 نکات مهم

1. **بکاپ بگیرید**: قبل از اجرای migration، حتماً از دیتابیس بکاپ بگیرید
2. **زمان مناسب**: migration را در ساعات کم‌ترافیک اجرا کنید
3. **بررسی لاگ**: بعد از اجرا، لاگ‌ها را بررسی کنید
4. **تست**: بعد از migration، API را تست کنید

---

## 🎯 خلاصه سریع

**Dashboard:**
1. https://dashboard.scalingo.com
2. اپلیکیشن `mywebsite`
3. One-off containers
4. `python manage.py migrate accounts`
5. Run

**CLI:**
```powershell
scalingo login
scalingo --app mywebsite run python manage.py migrate accounts
```

