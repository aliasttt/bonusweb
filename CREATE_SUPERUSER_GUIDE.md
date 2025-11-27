# راهنمای ساخت سوپر یوزر در Scalingo

## روش 1: ساخت دستی (پیشنهادی)

بعد از اینکه deployment تمام شد و migration اجرا شد:

```bash
# 1. اجرای migration
scalingo --app mywebsite run python manage.py migrate

# 2. ساخت سوپر یوزر (تعاملی)
scalingo --app mywebsite run python manage.py createsuperuser
```

سپس اطلاعات را وارد کن:
- Username: (مثلاً `admin`)
- Email: (مثلاً `admin@example.com`)
- Password: (رمز عبور قوی)

## روش 2: ساخت خودکار با اسکریپت

```powershell
.\create_superuser_scalingo.ps1 -Username "admin" -Email "admin@example.com"
```

⚠️ **نکته**: این روش نیاز به تنظیم password دارد که باید بعداً تغییر بدی.

## روش 3: ساخت از طریق Django Shell

```bash
scalingo --app mywebsite run python manage.py shell
```

سپس در shell:
```python
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'your_password')
exit()
```

## بررسی سوپر یوزر

برای بررسی اینکه سوپر یوزر ساخته شده:

```bash
scalingo --app mywebsite run python manage.py shell
```

سپس:
```python
from django.contrib.auth.models import User
print(User.objects.filter(is_superuser=True).count())
exit()
```

## تغییر رمز عبور

اگر رمز عبور را فراموش کردی:

```bash
scalingo --app mywebsite run python manage.py changepassword admin
```

## نکات مهم:

1. ⚠️ **قبل از ساخت سوپر یوزر**: مطمئن شو که migration اجرا شده
2. ✅ **بعد از ساخت**: می‌توانی از `/admin/` لاگین کنی
3. 🔒 **امنیت**: رمز عبور قوی انتخاب کن










