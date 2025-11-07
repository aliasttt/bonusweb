# 📋 راهنمای کامل Migration در Scalingo

## 🎯 هدف

این فایل راهنمای کامل برای اجرای migration در Scalingo است.

## ⚡ روش سریع (Dashboard)

**بدون نیاز به نصب CLI:**

1. به https://dashboard.scalingo.com بروید
2. اپلیکیشن `mywebsite` را انتخاب کنید
3. به بخش **"One-off containers"** بروید
4. دستور زیر را وارد کنید:
   ```
   python manage.py migrate accounts
   ```
5. روی **"Run"** کلیک کنید

✅ **تمام!**

---

## 🔧 روش CLI (برای استفاده مداوم)

### نصب Scalingo CLI:

1. **دانلود:**
   - به https://cli.scalingo.com/install بروید
   - یا مستقیماً: https://github.com/Scalingo/cli/releases/latest/download/scalingo_windows_amd64.exe

2. **نصب:**
   - فایل را در یک مسیر مناسب قرار دهید (مثلاً `C:\Program Files\Scalingo\`)
   - مسیر را به PATH اضافه کنید

3. **اجرای اسکریپت:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File run_migration_if_cli_installed.ps1
   ```

---

## 📁 فایل‌های موجود

- **MIGRATE_NOW.md** - راهنمای سریع
- **run_migration_if_cli_installed.ps1** - اسکریپت اجرای migration (اگر CLI نصب باشد)
- **auto_migrate.ps1** - اسکریپت کامل (دانلود، نصب، اجرا)
- **INSTALL_SCALINGO_CLI.md** - راهنمای نصب CLI
- **QUICK_MIGRATION_GUIDE.md** - راهنمای سریع

---

## 🚀 دستورات سریع

```powershell
# اگر CLI نصب است:
powershell -ExecutionPolicy Bypass -File run_migration_if_cli_installed.ps1

# یا دستی:
scalingo login
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## ✅ بررسی نتیجه

بعد از اجرای migration، بررسی کنید:

```powershell
scalingo --app mywebsite run python manage.py showmigrations accounts
```

باید همه migration ها با `[X]` علامت‌گذاری شده باشند.

---

## 🆘 مشکل دارید؟

1. **CLI نصب نیست:** از Dashboard استفاده کنید (روش 1)
2. **لاگین نیستید:** `scalingo login` را اجرا کنید
3. **خطا می‌گیرید:** لاگ‌ها را بررسی کنید: `scalingo --app mywebsite logs`

---

## 📌 نکات مهم

- قبل از migration، از دیتابیس بکاپ بگیرید
- migration را در ساعات کم‌ترافیک اجرا کنید
- بعد از migration، API را تست کنید

