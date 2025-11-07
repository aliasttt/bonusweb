# راهنمای سریع اجرای Migration در Scalingo

## ⚡ روش سریع (Dashboard - بدون نصب)

1. به https://dashboard.scalingo.com بروید
2. اپلیکیشن `mywebsite` را انتخاب کنید
3. به بخش **"One-off containers"** بروید
4. دستور زیر را وارد کنید:
   ```
   python manage.py migrate accounts
   ```
5. روی **"Run"** کلیک کنید

✅ **تمام!** Migration اجرا می‌شود.

---

## 🔧 روش CLI (برای استفاده مداوم)

### نصب Scalingo CLI:

1. دانلود از: https://cli.scalingo.com/install
2. فایل را اجرا کنید
3. مسیر را به PATH اضافه کنید

### اجرای Migration:

```powershell
# لاگین
scalingo login

# اجرای migration
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## 📝 نام اپلیکیشن

نام اپلیکیشن شما: **`mywebsite`**

اگر نام متفاوت است، در دستورات بالا `mywebsite` را با نام واقعی جایگزین کنید.

---

## ✅ بررسی نتیجه

بعد از اجرای migration، می‌توانید با دستور زیر بررسی کنید:

```powershell
scalingo --app mywebsite run python manage.py showmigrations accounts
```

باید همه migration ها با `[X]` علامت‌گذاری شده باشند.

