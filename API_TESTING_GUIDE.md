# 🧪 راهنمای تست API ها

این فایل شامل تمام URLهای API و نحوه تست آنهاست.

**Base URL**: `http://127.0.0.1:8000` (برای development)  
**Base URL**: `https://your-server.com` (برای production)

---

## 📋 فهرست تمام Endpoint ها

### 🔐 بخش احراز هویت (Accounts)

#### POST `/api/accounts/register/` - ثبت نام کاربر جدید
**URL کامل**: `http://127.0.0.1:8000/api/accounts/register/`

**⚠️ نکته مهم**: این endpoint **فقط با POST کار می‌کند**. استفاده از GET باعث خطای `405 Method Not Allowed` می‌شود.

**بدنه (Request Body)**:
```json
{
  "username": "testuser123",
  "password": "TestPass123!",
  "password_confirm": "TestPass123!",
  "email": "test@example.com",
  "first_name": "علی",
  "last_name": "احمدی",
  "phone": "09123456789"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "email": "test@example.com",
    "first_name": "علی",
    "last_name": "احمدی",
    "phone": "09123456789"
  }'
```

**تست با Postman**:
- Method: POST
- URL: `http://127.0.0.1:8000/api/accounts/register/`
- Headers: `Content-Type: application/json`
- Body (raw JSON): بالا

**پاسخ (Response) - 201 Created**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "testuser123",
    "first_name": "علی",
    "last_name": "احمدی",
    "email": "test@example.com",
    "date_joined": "2025-01-11T12:00:00Z",
    "is_active": true
  },
  "profile": {
    "id": 1,
    "role": "customer",
    "phone": "09123456789",
    "is_active": true,
    "created_at": "2025-01-11T12:00:00Z",
    "updated_at": "2025-01-11T12:00:00Z"
  }
}
```

**⚠️ نکته مهم**: بعد از ثبت نام موفق، توکن `access` و `refresh` در پاسخ برمی‌گردد. می‌توانید این توکن‌ها را برای احراز هویت در APIهای دیگر استفاده کنید.

---

#### POST `/api/accounts/token/` - دریافت JWT Token (لاگین)
**URL کامل**: `http://127.0.0.1:8000/api/accounts/token/`

**بدنه (Request Body)**:
```json
{
  "username": "testuser123",
  "password": "TestPass123!"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "password": "TestPass123!"
  }'
```

**پاسخ (Response)**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**⚠️ نکته**: `access` و `refresh` را برای تست APIهای دیگر ذخیره کنید.

---

#### POST `/api/accounts/token/refresh/` - تازه‌سازی Token
**URL کامل**: `http://127.0.0.1:8000/api/accounts/token/refresh/`

**بدنه (Request Body)**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN_HERE"
  }'
```

---

#### GET `/api/accounts/me/` - دریافت اطلاعات کاربر فعلی
**URL کامل**: `http://127.0.0.1:8000/api/accounts/me/`

**Headers** (الزامی):
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/accounts/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

#### POST `/api/accounts/users/<user_id>/role/` - تنظیم نقش کاربر (فقط SuperUser)
**URL کامل**: `http://127.0.0.1:8000/api/accounts/users/1/role/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "role": "customer"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/users/1/role/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "customer"
  }'
```

---

### 🏪 بخش کسب‌وکارها (Loyalty/Businesses)

#### GET `/api/businesses/` - دریافت لیست کسب‌وکارها
**URL کامل**: `http://127.0.0.1:8000/api/businesses/`

**احراز هویت**: ندارد

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/businesses/
```

**با Query Parameters**:
```bash
curl -X GET "http://127.0.0.1:8000/api/businesses/?is_active=true"
```

---

#### GET `/api/products/` - دریافت لیست محصولات
**URL کامل**: `http://127.0.0.1:8000/api/products/`

**احراز هویت**: ندارد

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/products/
```

**با Query Parameters**:
```bash
curl -X GET "http://127.0.0.1:8000/api/products/?business_id=1&active=true"
```

---

#### GET `/api/wallet/` - دریافت والت کاربر
**URL کامل**: `http://127.0.0.1:8000/api/wallet/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/wallet/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

### 📱 بخش امتیازها (Rewards)

#### POST `/api/rewards/scan-products/` - اسکن QR با محصولات
**URL کامل**: `http://127.0.0.1:8000/api/rewards/scan-products/`

**بدنه (Request Body)**:
```json
{
  "business_id": 1,
  "product_ids": [1, 2, 3],
  "phone": "09123456789"
}
```

**تست با curl** (بدون احراز هویت):
```bash
curl -X POST http://127.0.0.1:8000/api/rewards/scan-products/ \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1,
    "product_ids": [1, 2, 3],
    "phone": "09123456789"
  }'
```

**تست با curl** (با احراز هویت - phone نیاز نیست):
```bash
curl -X POST http://127.0.0.1:8000/api/rewards/scan-products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1,
    "product_ids": [1, 2, 3]
  }'
```

---

#### GET `/api/rewards/balance/` - دریافت موجودی امتیاز
**URL کامل**: `http://127.0.0.1:8000/api/rewards/balance/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/rewards/balance/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

#### GET `/api/rewards/history/` - دریافت تاریخچه امتیازها
**URL کامل**: `http://127.0.0.1:8000/api/rewards/history/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/rewards/history/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**با Query Parameters**:
```bash
curl -X GET "http://127.0.0.1:8000/api/rewards/history/?business_id=1&page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

#### POST `/api/rewards/scan/` - اسکن QR و دریافت امتیاز (قدیمی)
**URL کامل**: `http://127.0.0.1:8000/api/rewards/scan/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "token": "qr_token_here"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/rewards/scan/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "qr_token_here"
  }'
```

---

#### POST `/api/rewards/redeem/` - استفاده از امتیاز
**URL کامل**: `http://127.0.0.1:8000/api/rewards/redeem/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "business_id": 1,
  "amount": 10
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/rewards/redeem/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1,
    "amount": 10
  }'
```

---

### 📝 بخش نظرات (Reviews)

#### GET `/api/reviews/` - دریافت لیست نظرات
**URL کامل**: `http://127.0.0.1:8000/api/reviews/`

**احراز هویت**: ندارد

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/reviews/
```

**با Query Parameters**:
```bash
curl -X GET "http://127.0.0.1:8000/api/reviews/?business_id=1"
```

---

#### POST `/api/reviews/` - ثبت نظر جدید
**URL کامل**: `http://127.0.0.1:8000/api/reviews/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "business_id": 1,
  "rating": 5,
  "comment": "عالی بود!"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/reviews/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1,
    "rating": 5,
    "comment": "عالی بود!"
  }'
```

---

### 💳 بخش پرداخت (Payments)

#### GET `/api/payments/orders/` - دریافت لیست سفارشات
**URL کامل**: `http://127.0.0.1:8000/api/payments/orders/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/payments/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

#### POST `/api/payments/initiate/` - شروع پرداخت
**URL کامل**: `http://127.0.0.1:8000/api/payments/initiate/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "business_id": 1,
  "amount_cents": 50000,
  "currency": "IRR"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/payments/initiate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1,
    "amount_cents": 50000,
    "currency": "IRR"
  }'
```

---

### 🔔 بخش نوتیفیکیشن (Notifications)

#### POST `/api/notifications/register-device/` - ثبت دستگاه برای Push Notification
**URL کامل**: `http://127.0.0.1:8000/api/notifications/register-device/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "token": "fcm_device_token_here",
  "platform": "ios"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/notifications/register-device/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "fcm_device_token_here",
    "platform": "ios"
  }'
```

---

#### POST `/api/notifications/send-test/` - ارسال تست نوتیفیکیشن
**URL کامل**: `http://127.0.0.1:8000/api/notifications/send-test/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "title": "تست",
  "body": "این یک پیام تست است"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/notifications/send-test/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "تست",
    "body": "این یک پیام تست است"
  }'
```

---

### 📢 بخش کمپین‌ها (Campaigns)

#### GET `/api/campaigns/public/` - دریافت لیست کمپین‌های عمومی
**URL کامل**: `http://127.0.0.1:8000/api/campaigns/public/`

**احراز هویت**: ندارد

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/campaigns/public/
```

---

#### GET `/api/campaigns/` - دریافت لیست کمپین‌های کاربر
**URL کامل**: `http://127.0.0.1:8000/api/campaigns/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/campaigns/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

#### POST `/api/campaigns/` - ایجاد کمپین جدید
**URL کامل**: `http://127.0.0.1:8000/api/campaigns/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "name": "کمپین جدید",
  "description": "توضیحات کمپین",
  "business": 1,
  "points_per_scan": 5,
  "is_active": true
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/campaigns/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "کمپین جدید",
    "description": "توضیحات کمپین",
    "business": 1,
    "points_per_scan": 5,
    "is_active": true
  }'
```

---

#### GET `/api/campaigns/<pk>/` - دریافت جزئیات کمپین
**URL کامل**: `http://127.0.0.1:8000/api/campaigns/1/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/campaigns/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

#### PATCH `/api/campaigns/<pk>/` - به‌روزرسانی کمپین
**URL کامل**: `http://127.0.0.1:8000/api/campaigns/1/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "name": "کمپین به‌روز شده",
  "points_per_scan": 10
}
```

**تست با curl**:
```bash
curl -X PATCH http://127.0.0.1:8000/api/campaigns/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "کمپین به‌روز شده",
    "points_per_scan": 10
  }'
```

---

### 📱 بخش QR Code

#### GET `/api/qr/` - دریافت لیست QR Code ها
**URL کامل**: `http://127.0.0.1:8000/api/qr/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/qr/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

#### POST `/api/qr/` - ایجاد QR Code جدید
**URL کامل**: `http://127.0.0.1:8000/api/qr/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "business": 1,
  "campaign": 1
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/qr/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business": 1,
    "campaign": 1
  }'
```

---

#### GET `/api/qr/image/<token>.png` - دریافت تصویر QR Code
**URL کامل**: `http://127.0.0.1:8000/api/qr/image/abc123.png`

**احراز هویت**: ندارد

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/qr/image/abc123.png -o qr_code.png
```

---

#### POST `/api/qr/validate/` - اعتبارسنجی QR Code
**URL کامل**: `http://127.0.0.1:8000/api/qr/validate/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "token": "qr_token_here"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/qr/validate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "qr_token_here"
  }'
```

### 📊 بخش Analytics

#### POST `/api/analytics/ingest/` - ثبت رویداد آنالیتیک
**URL کامل**: `http://127.0.0.1:8000/api/analytics/ingest/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "event_type": "page_view",
  "event_data": {
    "page": "home",
    "user_id": 1
  }
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/analytics/ingest/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "page_view",
    "event_data": {
      "page": "home",
      "user_id": 1
    }
  }'
```

---

#### GET `/api/analytics/events/` - دریافت لیست رویدادها (Admin)
**URL کامل**: `http://127.0.0.1:8000/api/analytics/events/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/analytics/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

### 🔒 بخش Security

#### GET `/api/security/gdpr/export/` - دریافت داده‌های GDPR
**URL کامل**: `http://127.0.0.1:8000/api/security/gdpr/export/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**تست با curl**:
```bash
curl -X GET http://127.0.0.1:8000/api/security/gdpr/export/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

#### POST `/api/security/gdpr/delete/` - درخواست حذف داده‌های GDPR
**URL کامل**: `http://127.0.0.1:8000/api/security/gdpr/delete/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/security/gdpr/delete/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 🔑 بخش Loyalty (Token Endpoints)

#### POST `/api/auth/token/` - دریافت JWT Token (از Loyalty)
**URL کامل**: `http://127.0.0.1:8000/api/auth/token/`

**احراز هویت**: ندارد

**بدنه (Request Body)**:
```json
{
  "username": "testuser",
  "password": "TestPass123!"
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

**نکته**: این endpoint مشابه `/api/accounts/token/` است اما در مسیر `/api/auth/token/` قرار دارد.

---

#### POST `/api/auth/refresh/` - تازه‌سازی Token (از Loyalty)
**URL کامل**: `http://127.0.0.1:8000/api/auth/refresh/`

**احراز هویت**: ندارد

**بدنه (Request Body)**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN_HERE"
  }'
```

---

#### POST `/api/scan/` - اسکن Stamp (Loyalty)
**URL کامل**: `http://127.0.0.1:8000/api/scan/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "business_id": 1,
  "amount": 1
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/scan/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1,
    "amount": 1
  }'
```

---

#### POST `/api/redeem/` - استفاده از Reward (Loyalty)
**URL کامل**: `http://127.0.0.1:8000/api/redeem/`

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**بدنه (Request Body)**:
```json
{
  "business_id": 1
}
```

**تست با curl**:
```bash
curl -X POST http://127.0.0.1:8000/api/redeem/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1
  }'
```

---

## 📊 جدول خلاصه تمام Endpoint ها

| Method | Endpoint | Auth Required | توضیحات |
|--------|----------|---------------|---------|
| **POST** | `/api/accounts/register/` | ❌ | ثبت نام |
| **POST** | `/api/accounts/token/` | ❌ | لاگین |
| **POST** | `/api/accounts/token/refresh/` | ❌ | تازه‌سازی token |
| **GET** | `/api/accounts/me/` | ✅ | اطلاعات کاربر |
| **POST** | `/api/accounts/users/<id>/role/` | ✅ | تنظیم نقش |
| **GET** | `/api/businesses/` | ❌ | لیست کسب‌وکارها |
| **GET** | `/api/products/` | ❌ | لیست محصولات |
| **GET** | `/api/wallet/` | ✅ | والت کاربر |
| **POST** | `/api/rewards/scan-products/` | ⚠️ | اسکن QR (React Native) |
| **GET** | `/api/rewards/balance/` | ✅ | موجودی امتیاز |
| **GET** | `/api/rewards/history/` | ✅ | تاریخچه امتیاز |
| **POST** | `/api/rewards/scan/` | ✅ | اسکن QR (قدیمی) |
| **POST** | `/api/rewards/redeem/` | ✅ | استفاده از امتیاز |
| **GET** | `/api/reviews/` | ❌ | لیست نظرات |
| **POST** | `/api/reviews/` | ✅ | ثبت نظر |
| **GET** | `/api/payments/orders/` | ✅ | لیست سفارشات |
| **POST** | `/api/payments/initiate/` | ✅ | شروع پرداخت |
| **POST** | `/api/notifications/register-device/` | ✅ | ثبت دستگاه |
| **POST** | `/api/notifications/send-test/` | ✅ | تست نوتیفیکیشن |
| **GET** | `/api/campaigns/public/` | ❌ | کمپین‌های عمومی |
| **GET** | `/api/campaigns/` | ✅ | کمپین‌های کاربر |
| **POST** | `/api/campaigns/` | ✅ | ایجاد کمپین |
| **GET** | `/api/campaigns/<id>/` | ✅ | جزئیات کمپین |
| **PATCH** | `/api/campaigns/<id>/` | ✅ | به‌روزرسانی کمپین |
| **GET** | `/api/qr/` | ✅ | لیست QR Code |
| **POST** | `/api/qr/` | ✅ | ایجاد QR Code |
| **GET** | `/api/qr/image/<token>.png` | ❌ | تصویر QR Code |
| **POST** | `/api/qr/validate/` | ✅ | اعتبارسنجی QR Code |
| **POST** | `/api/analytics/ingest/` | ✅ | ثبت رویداد |
| **GET** | `/api/analytics/events/` | ✅ | لیست رویدادها |
| **GET** | `/api/security/gdpr/export/` | ✅ | دریافت داده GDPR |
| **POST** | `/api/security/gdpr/delete/` | ✅ | حذف داده GDPR |
| **POST** | `/api/auth/token/` | ❌ | لاگین (Loyalty) |
| **POST** | `/api/auth/refresh/` | ❌ | تازه‌سازی (Loyalty) |
| **POST** | `/api/scan/` | ✅ | اسکن Stamp (Loyalty) |
| **POST** | `/api/redeem/` | ✅ | استفاده از Reward (Loyalty) |

---

## 🔧 روش تست سریع

### 1. تست ثبت نام و لاگین:
```bash
# 1. ثبت نام
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123!", "password_confirm": "TestPass123!", "phone": "09123456789"}'

# 2. لاگین
curl -X POST http://127.0.0.1:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123!"}'
```

### 2. ذخیره Token برای تست‌های بعدی:
```bash
# در terminal یا PowerShell
export ACCESS_TOKEN="your_access_token_here"  # Linux/Mac
# یا
$env:ACCESS_TOKEN="your_access_token_here"  # Windows PowerShell
```

### 3. تست API با Token:
```bash
# در Linux/Mac
curl -X GET http://127.0.0.1:8000/api/accounts/me/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# در Windows PowerShell
curl -X GET http://127.0.0.1:8000/api/accounts/me/ \
  -H "Authorization: Bearer $env:ACCESS_TOKEN"
```

---

## 📚 استفاده از Swagger UI

برای مشاهده و تست تمام APIها از طریق رابط کاربری:

**URL**: `http://127.0.0.1:8000/api/docs/`

در این صفحه می‌توانید:
- تمام endpointها را ببینید
- مستقیماً تست کنید
- Response ها را مشاهده کنید
- Schema را ببینید

---

## ✅ چک‌لیست تست

- [ ] ثبت نام کاربر جدید
- [ ] لاگین و دریافت token
- [ ] دریافت اطلاعات کاربر (`/accounts/me/`)
- [ ] دریافت لیست کسب‌وکارها
- [ ] دریافت لیست محصولات
- [ ] اسکن QR با محصولات (با و بدون phone)
- [ ] دریافت موجودی امتیاز
- [ ] دریافت تاریخچه امتیاز
- [ ] استفاده از امتیاز (redeem)
- [ ] ثبت نظر
- [ ] دریافت نظرات
- [ ] شروع پرداخت
- [ ] ثبت دستگاه برای نوتیفیکیشن

---

**نکته**: برای تست‌های سریع‌تر می‌توانید از Postman یا Insomnia استفاده کنید.

