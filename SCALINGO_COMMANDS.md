# دستورات Scalingo CLI

## 1. لاگین به Scalingo

```powershell
scalingo login
```

بعد از اجرای این دستور:
- Username: `aliasttt`
- Password: `Aasadi2233#`

---

## 2. بررسی لاگین بودن

```powershell
scalingo whoami
```

---

## 3. بررسی وضعیت Migration ها

```powershell
scalingo --app mywebsite run python manage.py showmigrations accounts
```

---

## 4. اجرای Migration

```powershell
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## 5. اجرای همه Migration ها

```powershell
scalingo --app mywebsite run python manage.py migrate
```

---

## 6. مشاهده لاگ‌ها

```powershell
scalingo --app mywebsite logs
```

---

## 7. مشاهده لاگ‌های Real-time

```powershell
scalingo --app mywebsite logs --follow
```

---

## دستورات کامل (Copy-Paste)

### لاگین:
```powershell
scalingo login
```

### اجرای Migration:
```powershell
scalingo --app mywebsite run python manage.py migrate accounts
```

---

## نکات:

- نام اپلیکیشن: `mywebsite`
- اگر نام اپلیکیشن متفاوت است، `mywebsite` را با نام واقعی جایگزین کنید
- بعد از لاگین، می‌توانید migration را اجرا کنید

