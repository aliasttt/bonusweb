# راهنمای اجرای Migration در Scalingo

## روش 1: استفاده از Scalingo CLI (توصیه می‌شود)

### مرحله 1: نصب Scalingo CLI

**Windows:**
```powershell
# دانلود از: https://cli.scalingo.com/install
# یا استفاده از Chocolatey:
choco install scalingo-cli
```

**Mac:**
```bash
brew tap scalingo/scalingo
brew install scalingo
```

**Linux:**
```bash
curl -O https://cli.scalingo.com/install
bash install
```

### مرحله 2: لاگین به Scalingo

```bash
scalingo login
```

### مرحله 3: اجرای Migration

```bash
# نام اپلیکیشن شما: mywebsite
scalingo --app mywebsite run python manage.py migrate
```

یا اگر می‌خواهید فقط migration های accounts را اجرا کنید:

```bash
scalingo --app mywebsite run python manage.py migrate accounts
```

### مرحله 4: بررسی وضعیت Migration

```bash
scalingo --app mywebsite run python manage.py showmigrations
```

---

## روش 2: استفاده از One-Off Container (دسترسی به Shell)

اگر می‌خواهید به shell سرور دسترسی داشته باشید:

```bash
# اتصال به shell سرور
scalingo --app mywebsite run bash
```

سپس در shell:

```bash
# بررسی وضعیت migration ها
python manage.py showmigrations accounts

# اجرای migration
python manage.py migrate

# یا فقط accounts
python manage.py migrate accounts
```

---

## روش 3: استفاده از Dashboard Scalingo

1. به Scalingo Dashboard بروید: https://dashboard.scalingo.com
2. اپلیکیشن `mywebsite` را انتخاب کنید
3. به بخش **"One-off containers"** یا **"Run command"** بروید
4. دستور زیر را وارد کنید:
   ```
   python manage.py migrate
   ```
5. روی **"Run"** کلیک کنید

---

## نکات مهم:

1. **بکاپ بگیرید**: قبل از اجرای migration، حتماً از دیتابیس بکاپ بگیرید
2. **زمان مناسب**: migration را در ساعات کم‌ترافیک اجرا کنید
3. **بررسی لاگ**: بعد از اجرا، لاگ‌ها را بررسی کنید
4. **تست**: بعد از migration، API را تست کنید

---

## دستورات مفید:

```bash
# بررسی وضعیت migration ها
scalingo --app mywebsite run python manage.py showmigrations

# اجرای migration
scalingo --app mywebsite run python manage.py migrate

# اجرای migration خاص
scalingo --app mywebsite run python manage.py migrate accounts

# مشاهده لاگ‌ها
scalingo --app mywebsite logs

# مشاهده لاگ‌های real-time
scalingo --app mywebsite logs --follow
```

---

## در صورت خطا:

اگر خطا گرفتید، می‌توانید:

1. **بررسی لاگ‌ها:**
   ```bash
   scalingo --app mywebsite logs --lines 100
   ```

2. **بررسی وضعیت دیتابیس:**
   ```bash
   scalingo --app mywebsite run python manage.py dbshell
   ```

3. **بررسی migration ها:**
   ```bash
   scalingo --app mywebsite run python manage.py showmigrations accounts
   ```

