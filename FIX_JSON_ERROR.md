# 🔧 رفع خطای "This field is required"

اگر خطای زیر را دریافت کردی:
```json
{
  "error": "{'username': [ErrorDetail(string='This field is required.', code='required')], ...}"
}
```

این یعنی JSON به درستی ارسال نشده است.

---

## ✅ راه‌حل‌های تست شده

### روش 1: Windows PowerShell (توصیه می‌شود)

```powershell
# ثبت نام
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

### روش 2: استفاده از Invoke-WebRequest

```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    username = "testuser"
    password = "TestPass123!"
    password_confirm = "TestPass123!"
    phone = "09123456789"
} | ConvertTo-Json

$response = Invoke-WebRequest -Method POST `
  -Uri "http://127.0.0.1:8000/api/accounts/register/" `
  -Headers $headers `
  -Body $body

$response.Content
```

### روش 3: استفاده از Postman (آسان‌ترین روش)

1. دانلود و نصب Postman
2. Method را روی **POST** تنظیم کن
3. URL را وارد کن: `http://127.0.0.1:8000/api/accounts/register/`
4. در تب **Headers** اضافه کن:
   - Key: `Content-Type`
   - Value: `application/json`
5. در تب **Body**:
   - گزینه **raw** را انتخاب کن
   - در dropdown سمت راست **JSON** را انتخاب کن
6. JSON را وارد کن:
```json
{
  "username": "testuser",
  "password": "TestPass123!",
  "password_confirm": "TestPass123!",
  "phone": "09123456789"
}
```
7. روی **Send** کلیک کن

---

## 🐛 اشکال‌زدایی

### چک 1: Content-Type تنظیم شده است؟

```powershell
# بررسی Headers
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "Headers:"
$headers | ConvertTo-Json
```

### چک 2: JSON درست است؟

```powershell
$body = @{
    username = "testuser"
    password = "TestPass123!"
    password_confirm = "TestPass123!"
    phone = "09123456789"
} | ConvertTo-Json

Write-Host "Body:"
Write-Host $body
```

**خروجی باید اینطوری باشد**:
```json
{
  "username": "testuser",
  "password": "TestPass123!",
  "password_confirm": "TestPass123!",
  "phone": "09123456789"
}
```

### چک 3: همه فیلدهای required ارسال شده‌اند؟

**فیلدهای الزامی برای `/api/accounts/register/`**:
- ✅ `username` (string, required)
- ✅ `password` (string, required)
- ✅ `password_confirm` (string, required)
- ❌ `email` (optional)
- ❌ `first_name` (optional)
- ❌ `last_name` (optional)
- ❌ `phone` (optional)

**حداقل برای تست**:
```json
{
  "username": "testuser",
  "password": "TestPass123!",
  "password_confirm": "TestPass123!"
}
```

---

## 📝 مثال کامل تست در PowerShell

```powershell
# تنظیمات
$baseUrl = "http://127.0.0.1:8000"
$apiUrl = "$baseUrl/api/accounts/register/"

# آماده کردن Body
$registerData = @{
    username = "testuser_$(Get-Date -Format 'yyyyMMddHHmmss')"
    password = "TestPass123!"
    password_confirm = "TestPass123!"
    phone = "09123456789"
}

# تبدیل به JSON
$jsonBody = $registerData | ConvertTo-Json

# نمایش JSON (برای بررسی)
Write-Host "Sending JSON:"
Write-Host $jsonBody
Write-Host ""

# ارسال درخواست
try {
    $response = Invoke-RestMethod -Method POST `
        -Uri $apiUrl `
        -ContentType "application/json" `
        -Body $jsonBody
    
    Write-Host "Success! Response:"
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "Error occurred!"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error Message:"
    $_.ErrorDetails.Message
}
```

---

## 🔍 بررسی Response

### Response موفق (201 Created):
```json
{
  "user": {
    "id": 5,
    "username": "testuser",
    "first_name": "",
    "last_name": "",
    "email": "",
    "date_joined": "2025-11-02T19:51:03Z",
    "is_active": true
  },
  "profile": {
    "id": 1,
    "role": "customer",
    "phone": "09123456789",
    "is_active": true,
    ...
  }
}
```

### Response خطا (400 Bad Request):
```json
{
  "error": "{'username': [ErrorDetail(string='This field is required.', code='required')], ...}"
}
```

یا:
```json
{
  "password_confirm": ["Passwords don't match"]
}
```

---

## ✅ راه‌حل سریع (Copy-Paste)

کپی کن و اجرا کن در PowerShell:

```powershell
$body = @{
    username = "testuser"
    password = "TestPass123!"
    password_confirm = "TestPass123!"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/accounts/register/" `
  -ContentType "application/json" `
  -Body $body
```

---

## 💡 استفاده از Swagger UI (آسان‌ترین)

1. مرورگر را باز کن
2. به این آدرس برو: `http://127.0.0.1:8000/api/docs/`
3. endpoint `/api/accounts/register/` را پیدا کن
4. روی **Try it out** کلیک کن
5. فیلدها را پر کن
6. روی **Execute** کلیک کن

این ساده‌ترین روش برای تست API است!

---

**نکته**: اگر هنوز خطا می‌گیری، مطمئن شو که:
1. ✅ Server در حال اجرا است (`python manage.py runserver`)
2. ✅ URL درست است (`http://127.0.0.1:8000/api/accounts/register/`)
3. ✅ Method روی POST است
4. ✅ Content-Type: application/json تنظیم شده
5. ✅ JSON syntax درست است (بدون trailing comma)



