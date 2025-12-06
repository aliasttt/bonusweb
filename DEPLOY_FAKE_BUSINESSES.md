# راهنمای اضافه کردن بیزینس‌های فیک به Scalingo

## روش 1: اجرا از طریق Scalingo CLI

```bash
# اتصال به Scalingo
scalingo --app your-app-name run python manage.py add_fake_businesses
```

## روش 2: اجرا از طریق Django Admin Console

1. وارد پنل Scalingo شوید
2. به بخش "Console" بروید
3. دستور زیر را اجرا کنید:
```bash
python manage.py add_fake_businesses
```

## روش 3: اجرا از طریق SSH

اگر SSH دسترسی دارید:
```bash
ssh your-app@ssh.scalingo.com
python manage.py add_fake_businesses
```

## نکات مهم:

- ✅ اسکریپت فقط بیزینس‌های جدید اضافه می‌کند (اگر قبلاً وجود داشته باشند، اضافه نمی‌کند)
- ✅ عکس‌ها از Unsplash دانلود می‌شوند و در media storage ذخیره می‌شوند
- ✅ می‌توانید بعداً از پنل ادمین حذف کنید

