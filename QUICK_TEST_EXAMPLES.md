# ⚡ مثال‌های سریع تست API

این فایل شامل دستورات curl آماده برای تست سریع APIهاست.

**Base URL**: `http://127.0.0.1:8000`

---

## ⚠️ نکات مهم

1. **همیشه از POST برای ثبت نام و لاگین استفاده کن** - استفاده از GET باعث خطای `405 Method Not Allowed` می‌شود
2. **برای APIهایی که نیاز به احراز هویت دارند، token را در header بفرست**
3. **Content-Type را همیشه روی `application/json` تنظیم کن**

---

## 🔐 ثبت نام و لاگین (بدون token)

### 1. ثبت نام کاربر جدید

**⚠️ مهم**: حتماً `Content-Type: application/json` را در header اضافه کن و JSON را درست ارسال کن.

#### روش 1: Linux/Mac (bash)
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123!", "password_confirm": "TestPass123!", "phone": "09123456789"}'
```

#### روش 2: Windows PowerShell (توصیه می‌شود)
```powershell
$body = @{
    username = "testuser"
    password = "TestPass123!"
    password_confirm = "TestPass123!"
    phone = "09123456789"
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/accounts/register/" `
  -ContentType "application/json" `
  -Body $body
```

#### روش 3: Windows PowerShell (با string JSON)
```powershell
$jsonBody = '{"username": "testuser", "password": "TestPass123!", "password_confirm": "TestPass123!", "phone": "09123456789"}'

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/accounts/register/" `
  -ContentType "application/json" `
  -Body $jsonBody
```

#### روش 4: Windows CMD (با curl.exe)
```cmd
curl.exe -X POST http://127.0.0.1:8000/api/accounts/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"testuser\", \"password\": \"TestPass123!\", \"password_confirm\": \"TestPass123!\", \"phone\": \"09123456789\"}"
```

#### روش 5: استفاده از فایل JSON
ابتدا یک فایل `register.json` بساز:
```json
{
  "username": "testuser",
  "password": "TestPass123!",
  "password_confirm": "TestPass123!",
  "phone": "09123456789"
}
```

سپس:
```bash
# Linux/Mac
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d @register.json
```

```powershell
# Windows PowerShell
$body = Get-Content register.json -Raw
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/accounts/register/" `
  -ContentType "application/json" `
  -Body $body
```

---

### 2. لاگین و دریافت Token

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"testuser\", \"password\": \"TestPass123!\"}"
```

**پاسخ**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**⚠️ مهم**: `access` token را کپی کن و در دستورات بعدی استفاده کن.

---

## 🔑 تست با Token (بعد از لاگین)

### 3. دریافت اطلاعات کاربر

```bash
# Linux/Mac
curl -X GET http://127.0.0.1:8000/api/accounts/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**PowerShell (Windows)**:
```powershell
curl -Method GET -Uri "http://127.0.0.1:8000/api/accounts/me/" `
  -Headers @{"Authorization"="Bearer YOUR_ACCESS_TOKEN_HERE"}
```

---

## 🏪 کسب‌وکارها (بدون token)

### 4. دریافت لیست کسب‌وکارها

```bash
curl -X GET http://127.0.0.1:8000/api/businesses/
```

---

### 5. دریافت لیست محصولات

```bash
curl -X GET http://127.0.0.1:8000/api/products/
```

**با فیلتر**:
```bash
curl -X GET "http://127.0.0.1:8000/api/products/?business_id=1&active=true"
```

---

## 📱 اسکن QR (بدون token - برای کاربر جدید)

### 6. اسکن QR با محصولات

```bash
curl -X POST http://127.0.0.1:8000/api/rewards/scan-products/ \
  -H "Content-Type: application/json" \
  -d "{\"business_id\": 1, \"product_ids\": [1, 2], \"phone\": \"09123456789\"}"
```

**PowerShell**:
```powershell
curl -Method POST -Uri "http://127.0.0.1:8000/api/rewards/scan-products/" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"business_id": 1, "product_ids": [1, 2], "phone": "09123456789"}'
```

---

## 📊 امتیازها (با token)

### 7. دریافت موجودی امتیاز

```bash
curl -X GET http://127.0.0.1:8000/api/rewards/balance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

### 8. دریافت تاریخچه امتیازها

```bash
curl -X GET http://127.0.0.1:8000/api/rewards/history/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

### 9. استفاده از امتیاز (Redeem)

```bash
curl -X POST http://127.0.0.1:8000/api/rewards/redeem/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"business_id\": 1, \"amount\": 10}"
```

---

## 📝 نظرات

### 10. دریافت لیست نظرات (بدون token)

```bash
curl -X GET http://127.0.0.1:8000/api/reviews/
```

---

### 11. ثبت نظر (با token)

```bash
curl -X POST http://127.0.0.1:8000/api/reviews/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"business_id\": 1, \"rating\": 5, \"comment\": \"عالی بود!\"}"
```

---

## 🔧 روش تست مرحله به مرحله

### مرحله 1: ثبت نام

```bash
# ثبت نام کاربر جدید
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123!", "password_confirm": "TestPass123!", "phone": "09123456789"}'
```

### مرحله 2: لاگین

```bash
# لاگین و دریافت token
curl -X POST http://127.0.0.1:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123!"}'
```

**نکته**: `access` token را از پاسخ کپی کن.

### مرحله 3: تست با Token

```bash
# تست اطلاعات کاربر
curl -X GET http://127.0.0.1:8000/api/accounts/me/ \
  -H "Authorization: Bearer PASTE_YOUR_ACCESS_TOKEN_HERE"
```

---

## 🐛 رفع خطاهای رایج

### خطای 405 Method Not Allowed

**مشکل**: استفاده از GET برای endpoint که فقط POST می‌پذیرد

**راه‌حل**: از POST استفاده کن
```bash
# ❌ اشتباه
curl -X GET http://127.0.0.1:8000/api/accounts/register/

# ✅ درست
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "Test123!", "password_confirm": "Test123!"}'
```

---

### خطای 401 Unauthorized

**مشکل**: Token ارسال نشده یا نامعتبر است

**راه‌حل**: 
1. ابتدا لاگین کن و token دریافت کن
2. Token را در header `Authorization: Bearer <token>` بفرست

---

### خطای 400 Bad Request

**مشکل**: فیلدهای لازم ارسال نشده یا نامعتبر است

**راه‌حل**: 
- بررسی کن که همه فیلدهای required ارسال شده‌اند
- بررسی کن که JSON format درست است
- بررسی کن که Content-Type روی `application/json` تنظیم شده

---

## 📋 چک‌لیست سریع

- [ ] ثبت نام موفق
- [ ] لاگین و دریافت token
- [ ] تست `/api/accounts/me/` با token
- [ ] دریافت لیست کسب‌وکارها
- [ ] اسکن QR (با و بدون token)
- [ ] دریافت موجودی امتیاز
- [ ] ثبت نظر

---

## 💡 نکات برای Windows PowerShell

در PowerShell، استفاده از single quotes (`'`) برای JSON بهتر است:

```powershell
# درست ✅
curl -Method POST -Uri "http://127.0.0.1:8000/api/accounts/register/" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username": "test", "password": "Test123!", "password_confirm": "Test123!"}'

# اشتباه ❌ (اگر از double quotes استفاده کنی، باید escape کنی)
curl -Method POST -Uri "http://127.0.0.1:8000/api/accounts/register/" `
  -Headers @{"Content-Type"="application/json"} `
  -Body "{\"username\": \"test\", \"password\": \"Test123!\", \"password_confirm\": \"Test123!\"}"
```

---

**نکته**: برای تست راحت‌تر، می‌توانی از Postman یا Insomnia استفاده کنی که رابط کاربری بهتری دارند.

