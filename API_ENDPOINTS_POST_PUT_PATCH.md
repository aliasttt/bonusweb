# لیست API های POST/PUT/PATCH

## 🔐 Accounts API (`/api/accounts/`)

### POST `/api/accounts/register/`
- **توضیحات**: ثبت نام کاربر جدید
- **احراز هویت**: ندارد
- **بدنه**: `{username, email, password, phone?, role?}`

### POST `/api/accounts/token/`
- **توضیحات**: دریافت JWT Token
- **احراز هویت**: ندارد
- **بدنه**: `{username, password}`

### POST `/api/accounts/token/refresh/`
- **توضیحات**: رفرش JWT Token
- **احراز هویت**: ندارد
- **بدنه**: `{refresh}`

### POST `/api/accounts/users/<user_id>/role/`
- **توضیحات**: تنظیم نقش کاربر (فقط SuperUser)
- **احراز هویت**: نیاز دارد + SuperUser
- **بدنه**: `{role}`

### POST `/api/accounts/users/<id>/activate/`
- **توضیحات**: فعال/غیرفعال کردن کاربر (فقط SuperUser)
- **احراز هویت**: نیاز دارد + SuperUser
- **بدنه**: `{is_active: true/false}`

### POST/PUT/PATCH/DELETE `/api/accounts/users/`
- **توضیحات**: مدیریت کاربران (ViewSet) - فقط SuperUser
- **احراز هویت**: نیاز دارد + SuperUser

### POST/PUT/PATCH/DELETE `/api/accounts/businesses/`
- **توضیحات**: مدیریت کسب‌وکارها (ViewSet) - Admin یا بالاتر
- **احراز هویت**: نیاز دارد + Admin

---

## 📢 Campaigns API (`/api/campaigns/`)

### POST `/api/campaigns/`
- **توضیحات**: ایجاد کمپین جدید
- **احراز هویت**: نیاز دارد + BusinessOwner
- **بدنه**: `{name, description, business, points_per_scan?, is_active?}`

### PATCH/PUT `/api/campaigns/<pk>/`
- **توضیحات**: به‌روزرسانی کمپین
- **احراز هویت**: نیاز دارد + BusinessOwner یا Admin

---

## 📱 QR Code API (`/api/qr/`)

### POST `/api/qr/`
- **توضیحات**: ایجاد QR Code جدید
- **احراز هویت**: نیاز دارد + BusinessOwner
- **بدنه**: `{business, campaign?}`

### POST `/api/qr/validate/`
- **توضیحات**: اعتبارسنجی QR Code
- **احراز هویت**: نیاز دارد
- **بدنه**: `{token}`

### POST `/api/qr/payment/`
- **توضیحات**: پردازش پرداخت QR (ایجاد Transaction و Stamps)
- **احراز هویت**: نیاز دارد
- **بدنه**: `{token, amount?, note?, business_password?}`

### POST `/api/qr/redeem/`
- **توضیحات**: استفاده از پاداش (reset stamps)
- **احراز هویت**: نیاز دارد
- **بدنه**: `{business_id}`

---

## 🎁 Rewards API (`/api/rewards/`)

### POST `/api/rewards/scan-products/` ⭐ **جدید برای React Native**
- **توضیحات**: اسکن QR با business_id و product_ids - اگر کاربر جدید بود با شماره تلفن ثبت نام می‌کند
- **احراز هویت**: ندارد (برای کاربران جدید)
- **بدنه**: `{business_id, product_ids: [1, 2, 3], phone: "09123456789"}`
- **Response**: `{success, is_new_user, user_id, customer_id, business_id, business_name, products: [...], total_points_awarded, current_balance, transaction_id, wallet_id}`

### POST `/api/rewards/scan/`
- **توضیحات**: اسکن QR و دریافت امتیاز
- **احراز هویت**: نیاز دارد + Customer
- **بدنه**: `{token}`

### POST `/api/rewards/redeem/`
- **توضیحات**: استفاده از امتیاز
- **احراز هویت**: نیاز دارد + Customer
- **بدنه**: `{business_id, amount}`

---

## ⭐ Reviews API (`/api/reviews/`)

### POST `/api/reviews/`
- **توضیحات**: ثبت نظر جدید
- **احراز هویت**: نیاز دارد
- **بدنه**: `{business_id, rating, comment?}`

---

## 💳 Payments API (`/api/payments/`)

### POST `/api/payments/initiate/`
- **توضیحات**: شروع پرداخت (ایجاد Order و PaymentIntent)
- **احراز هویت**: نیاز دارد
- **بدنه**: `{business_id, amount_cents, currency?}`

### POST `/api/payments/stripe/webhook/`
- **توضیحات**: وب‌هوک Stripe برای به‌روزرسانی وضعیت Order
- **احراز هویت**: ندارد (فقط Stripe)

---

## 📊 Analytics API (`/api/analytics/`)

### POST `/api/analytics/ingest/`
- **توضیحات**: ثبت رویداد آنالیتیک
- **احراز هویت**: نیاز دارد
- **بدنه**: `{event_type, event_data?, ...}`

---

## 🔔 Notifications API (`/api/notifications/`)

### POST `/api/notifications/register-device/`
- **توضیحات**: ثبت دستگاه برای Push Notification (FCM)
- **احراز هویت**: نیاز دارد
- **بدنه**: `{token, platform?}`

### POST `/api/notifications/send-test/`
- **توضیحات**: ارسال تست نوتیفیکیشن
- **احراز هویت**: نیاز دارد
- **بدنه**: `{title?, body?}`

---

## 🔒 Security API (`/api/security/`)

### POST `/api/security/gdpr/delete/`
- **توضیحات**: درخواست حذف داده‌های GDPR
- **احراز هویت**: نیاز دارد
- **بدنه**: `{}`

---

## 🏪 Loyalty API (`/api/`)

### POST `/api/scan/`
- **توضیحات**: اسکن و اضافه کردن Stamp
- **احراز هویت**: نیاز دارد
- **بدنه**: `{business_id, amount?}`

### POST `/api/redeem/`
- **توضیحات**: استفاده از Reward (reset stamps)
- **احراز هویت**: نیاز دارد
- **بدنه**: `{business_id}`

---

## 📝 Partners Portal (نیاز به لاگین HTML)

### POST `/partners/products/new/`
- **توضیحات**: ایجاد محصول جدید
- **احراز هویت**: نیاز دارد (Session)
- **فرم**: `{title, price_cents, points_reward, image?}`

### POST `/partners/products/<pk>/edit/`
- **توضیحات**: ویرایش محصول
- **احراز هویت**: نیاز دارد (Session)
- **فرم**: `{title, price_cents, points_reward, image?}`

### POST `/partners/settings/`
- **توضیحات**: به‌روزرسانی تنظیمات کسب‌وکار
- **احراز هویت**: نیاز دارد (Session)
- **فرم**: `{name, description, address, website, free_reward_threshold}`

---

## 🔑 توجه

- همه API های REST نیاز به `Authorization: Bearer <token>` دارند (مگر اینکه گفته شده باشد)
- Partners Portal از Session-based authentication استفاده می‌کند
- برای تست می‌توانید از `/api/docs/` (Swagger) استفاده کنید

