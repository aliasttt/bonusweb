# اجرای فوری Migration برای رفع خطای interests

## ⚠️ مشکل فعلی
خطای `no such column: accounts_profile.interests` به این دلیل است که migration روی دیتابیس production اجرا نشده است.

## ✅ راه حل سریع: استفاده از Dashboard Scalingo

### مرحله 1: ورود به Dashboard
1. به آدرس زیر بروید: **https://dashboard.scalingo.com**
2. لاگین کنید

### مرحله 2: انتخاب اپلیکیشن
1. اپلیکیشن **`mywebsite`** را انتخاب کنید

### مرحله 3: اجرای Migration
1. به بخش **"One-off containers"** یا **"Run command"** بروید
2. دستور زیر را وارد کنید:
   ```
   python manage.py migrate accounts
   ```
3. روی **"Run"** کلیک کنید

### مرحله 4: بررسی نتیجه
بعد از اجرا، باید پیام موفقیت را ببینید. سپس صفحه `/partners/dashboard/` را دوباره تست کنید.

---

## روش 2: نصب Scalingo CLI و اجرای دستور

### مرحله 1: نصب Scalingo CLI

**گزینه A: دانلود مستقیم**
1. به آدرس بروید: **https://cli.scalingo.com/install**
2. فایل نصب را دانلود و اجرا کنید

**گزینه B: استفاده از Chocolatey** (اگر نصب است)
```powershell
choco install scalingo-cli
```

### مرحله 2: لاگین
```powershell
scalingo login
```

### مرحله 3: اجرای Migration
```powershell
scalingo --app mywebsite run python manage.py migrate accounts
```

### مرحله 4: بررسی وضعیت
```powershell
scalingo --app mywebsite run python manage.py showmigrations accounts
```

باید `[X]` کنار `0004_profile_interests` ببینید.

---

## 📝 توضیحات

- Migration فایل `accounts/migrations/0004_profile_interests.py` وجود دارد
- این migration ستون `interests` را به جدول `accounts_profile` اضافه می‌کند
- بعد از اجرای migration، خطا برطرف می‌شود

---

## ⚡ روش سریع‌تر: Dashboard

**توصیه می‌شود از Dashboard استفاده کنید** چون:
- نیاز به نصب CLI ندارد
- سریع‌تر است
- رابط کاربری ساده‌ای دارد

---

## 🔍 بررسی بعد از Migration

بعد از اجرای migration، می‌توانید با دستور زیر بررسی کنید:

```powershell
scalingo --app mywebsite run python manage.py showmigrations accounts
```

یا در Dashboard:
```
python manage.py showmigrations accounts
```

باید همه migration ها با `[X]` علامت‌گذاری شده باشند.

