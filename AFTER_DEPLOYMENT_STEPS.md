# مراحل بعد از اتمام Deployment

## ⏳ منتظر بمان تا Deployment تمام شود

deployment در حال انجام است. بعد از اینکه status به `success` تغییر کرد، این مراحل را انجام بده:

## ✅ مراحل بعد از Deployment:

### 1. بررسی اینکه Deployment تمام شده:

```powershell
scalingo --app mywebsite deployments
```

باید آخرین deployment با status `success` باشد.

### 2. بررسی نصب psycopg2:

```powershell
.\check_deployment.ps1
```

یا دستی:
```powershell
# Create test file
echo "import psycopg2; print('OK')" > test.py
scalingo --app mywebsite run python test.py
del test.py
```

اگر `OK` چاپ شد، ادامه بده.

### 3. اجرای Migration:

```powershell
scalingo --app mywebsite run python manage.py migrate
```

### 4. ساخت سوپر یوزر:

**روش 1: تعاملی (پیشنهادی)**
```powershell
scalingo --app mywebsite run python manage.py createsuperuser
```

سپس اطلاعات را وارد کن:
- Username: `admin`
- Email: `admin@example.com`
- Password: (رمز قوی)

**روش 2: از طریق Shell**
```powershell
scalingo --app mywebsite run python manage.py shell
```

سپس در shell:
```python
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'your_password_here')
exit()
```

### 5. تست لاگین:

بعد از ساخت سوپر یوزر، به `/admin/` برو و لاگین کن.

## 🔍 بررسی وضعیت:

برای بررسی اینکه همه چیز درست کار می‌کند:

```powershell
# Check database connection
scalingo --app mywebsite run python manage.py dbshell

# Check superuser exists
scalingo --app mywebsite run python manage.py shell
# Then: User.objects.filter(is_superuser=True).count()
```

## ⚠️ نکات مهم:

1. **صبر کن**: deployment ممکن است 2-5 دقیقه طول بکشد
2. **ترتیب مهم است**: اول migration، بعد createsuperuser
3. **رمز قوی**: برای سوپر یوزر رمز قوی انتخاب کن

## 📝 خلاصه دستورات:

```powershell
# 1. Check deployment
scalingo --app mywebsite deployments

# 2. Run migration
scalingo --app mywebsite run python manage.py migrate

# 3. Create superuser
scalingo --app mywebsite run python manage.py createsuperuser
```






