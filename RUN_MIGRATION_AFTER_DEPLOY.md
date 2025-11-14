# 🚀 اجرای Migration بعد از Deploy

## وضعیت فعلی:

✅ تغییرات به git push شد  
⏳ منتظر deploy در Scalingo  
⏳ بعد از deploy، migration را اجرا کنید  

---

## مراحل:

### 1. منتظر بمانید تا Scalingo deploy کند

Scalingo معمولاً خودکار deploy می‌کند وقتی git push می‌کنید.  
می‌توانید در Dashboard Scalingo بررسی کنید که deploy انجام شده یا نه.

---

### 2. بعد از deploy، migration را اجرا کنید:

```powershell
# اضافه کردن به PATH
$env:Path += ";$env:USERPROFILE\AppData\Local\Programs\Scalingo"

# بررسی وضعیت migration ها
scalingo --app mywebsite run python manage.py showmigrations accounts

# اجرای migration
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## دستورات کامل:

```powershell
# 1. اضافه کردن به PATH
$env:Path += ";$env:USERPROFILE\AppData\Local\Programs\Scalingo"

# 2. بررسی وضعیت migration ها
scalingo --app mywebsite run python manage.py showmigrations accounts

# 3. اگر migration 0004_profile_interests را دیدید، اجرا کنید:
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## بررسی نتیجه:

بعد از اجرای migration، باید ببینید:

```
accounts
 [X] 0001_initial
 [X] 0002_profile_business_address_profile_business_name_and_more
 [X] 0003_emailverificationcode
 [X] 0004_profile_interests  ← این باید اضافه شود
```

---

## اگر migration اجرا نشد:

1. بررسی کنید که deploy انجام شده باشد
2. بررسی کنید که migration فایل در production هست
3. دوباره migration را اجرا کنید

---

## خلاصه:

1. ✅ تغییرات push شد
2. ⏳ منتظر deploy
3. ⏳ بعد از deploy، migration را اجرا کنید








