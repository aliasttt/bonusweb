# 📋 جزئیات فیلدهای API و ساختار دیتابیس

این فایل شامل جزئیات کامل فیلدهای هر API، ساختار دیتابیس و منطق کد است.

---

## 🔐 بخش احراز هویت و ثبت نام

### 1. `POST /api/accounts/register/` - ثبت نام کاربر جدید

#### 📝 فیلدهای Request (RegisterSerializer):

| فیلد | نوع | Required | توضیحات | محدودیت‌ها |
|------|-----|----------|---------|-----------|
| `number` | string | ✅ بله | شماره تلفن | باید unique باشد |
| `name` | string | ✅ بله | نام کاربر | به first_name و last_name تقسیم می‌شود |
| `email` | string | ✅ بله | ایمیل | EmailField format، باید unique باشد |
| `password` | string | ✅ بله | رمز عبور | validated by Django password validators |
| `confirmPassword` | string | ✅ بله | تکرار رمز عبور | باید با password مطابقت داشته باشد (با P بزرگ) |
| `favorit` | array[string] | ❌ خیر | لیست علاقه‌مندی‌ها | به صورت JSON در business_name ذخیره می‌شود |
| `last_name` | string | ❌ خیر | نام خانوادگی | allow_blank=True (اختیاری) |
| `role` | string | ❌ خیر | نقش کاربر | choices: "superuser", "admin", "business_owner", "customer" (default: "customer") |

#### 🔍 منطق کد (RegisterSerializer.create):

```python
# 1. password و confirmPassword بررسی و حذف می‌شوند
# 2. number (phone) بررسی می‌شود (باید unique باشد)
# 3. email بررسی می‌شود (باید unique باشد)
# 4. name به first_name و last_name تقسیم می‌شود
# 5. username از number ساخته می‌شود: "user_{number}"
# 6. User ایجاد می‌شود (email موقتاً خالی می‌ماند)
# 7. password با set_password hash می‌شود
# 8. Profile ایجاد/بازیابی می‌شود
# 9. profile.role تنظیم می‌شود (superuser نمی‌تواند role باشد)
# 10. profile.phone = number تنظیم می‌شود
# 11. favorit به صورت JSON در profile.business_name ذخیره می‌شود
```

#### 📊 فیلدهای Response:

**JWT Tokens:**
- `access`: string (JWT access token) - برای احراز هویت در درخواست‌های بعدی استفاده می‌شود
- `refresh`: string (JWT refresh token) - برای تازه‌سازی access token استفاده می‌شود

**User (UserSerializer):**
- `id`: integer (read_only)
- `username`: string
- `first_name`: string
- `last_name`: string
- `email`: string
- `date_joined`: datetime (read_only)
- `is_active`: boolean

**Profile (ProfileSerializer):**
- `id`: integer (read_only)
- `role`: string ("superuser" | "admin" | "business_owner" | "customer")
- `phone`: string (max_length=32, blank=True)
- `business_name`: string (max_length=200, blank=True)
- `is_active`: boolean (default=True)
- `last_login_ip`: IP address (read_only)
- `created_at`: datetime (read_only)
- `updated_at`: datetime (read_only)
- `business_type`: string (max_length=100, blank=True)
- `business_address`: text (blank=True)
- `business_phone`: string (max_length=32, blank=True)
- `total_logins`: integer (read_only)
- `last_activity`: datetime (read_only)

**✅ نکته مهم**: بعد از ثبت نام موفق (status 201)، توکن‌های JWT همراه با اطلاعات کاربر برمی‌گردند. نیازی به لاگین جداگانه نیست. می‌توانید مستقیماً از توکن‌ها برای احراز هویت استفاده کنید.

#### 🗄️ ساختار دیتابیس:

**User Model (Django built-in):**
- `id`: AutoField (Primary Key)
- `username`: CharField(max_length=150, unique=True)
- `password`: CharField(max_length=128)
- `email`: EmailField(blank=True)
- `first_name`: CharField(max_length=150, blank=True)
- `last_name`: CharField(max_length=150, blank=True)
- `date_joined`: DateTimeField(auto_now_add=True)
- `is_active`: BooleanField(default=True)

**Profile Model:**
- `id`: AutoField (Primary Key)
- `user`: OneToOneField(User, related_name="profile")
- `role`: CharField(max_length=32, choices=Role.choices, default=Role.CUSTOMER)
- `phone`: CharField(max_length=32, blank=True)
- `business_name`: CharField(max_length=200, blank=True)
- `is_active`: BooleanField(default=True)
- `last_login_ip`: GenericIPAddressField(null=True, blank=True)
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)
- `business_type`: CharField(max_length=100, blank=True)
- `business_address`: TextField(blank=True)
- `business_phone`: CharField(max_length=32, blank=True)
- `total_logins`: PositiveIntegerField(default=0)
- `last_activity`: DateTimeField(null=True, blank=True)

---

### 2. `POST /api/accounts/token/` - دریافت JWT Token (لاگین)

#### 📝 فیلدهای Request (TokenObtainPairView):

| فیلد | نوع | Required | توضیحات |
|------|-----|----------|---------|
| `username` | string | ✅ بله | نام کاربری یا شماره تلفن |
| `password` | string | ✅ بله | رمز عبور |

#### 📊 فیلدهای Response:

```json
{
  "access": "string (JWT token)",
  "refresh": "string (JWT refresh token)"
}
```

#### 🔍 منطق کد:
- از Django REST Framework SimpleJWT استفاده می‌کند
- username/password را بررسی می‌کند
- JWT access و refresh token برمی‌گرداند

---

### 3. `GET /api/accounts/me/` - دریافت اطلاعات کاربر فعلی

#### 📝 Headers:

| Header | نوع | Required | توضیحات |
|--------|-----|----------|---------|
| `Authorization` | string | ✅ بله | `Bearer <access_token>` |

#### 📊 فیلدهای Response:

**User (UserSerializer):**
- `id`: integer
- `username`: string
- `first_name`: string
- `last_name`: string
- `email`: string
- `date_joined`: datetime
- `is_active`: boolean

**Profile (ProfileSerializer):**
- تمام فیلدهای Profile (همان بالا)

---

## 🏪 بخش کسب‌وکارها

### 4. `GET /api/businesses/` - دریافت لیست کسب‌وکارها

#### 📝 Query Parameters:

| پارامتر | نوع | Required | توضیحات |
|---------|-----|----------|---------|
| `type` | string | ❌ خیر | فیلتر بر اساس نوع کسب‌وکار |
| `is_active` | boolean | ❌ خیر | فقط کسب‌وکارهای فعال |

#### 📊 فیلدهای Response (BusinessSerializer - loyalty):

**Business Model (loyalty/models.py):**
- `id`: integer
- `owner`: User (ForeignKey)
- `name`: string (max_length=200)
- `description`: text (blank=True)
- `address`: string (max_length=300, blank=True)
- `website`: URL (blank=True)
- `phone`: string (max_length=20, blank=True)
- `password`: string (max_length=128, blank=True, hashed)
- `reward_point_cost`: integer (default=100) — تعداد امتیاز لازم برای دریافت ریوارد
- `created_at`: datetime (auto_now_add=True)

#### 🗄️ ساختار دیتابیس Business (loyalty):

```python
class Business(models.Model):
    owner = ForeignKey(User)
    name = CharField(max_length=200)
    description = TextField(blank=True)
    address = CharField(max_length=300, blank=True)
    website = URLField(blank=True)
    phone = CharField(max_length=20, blank=True)
    password = CharField(max_length=128, blank=True)  # hashed
    reward_point_cost = PositiveIntegerField(default=100)
    created_at = DateTimeField(auto_now_add=True)
```

**نکته**: Business در دو جا تعریف شده:
1. `accounts/models.py` - برای مدیریت کاربران (Business with metrics)
2. `loyalty/models.py` - برای سیستم وفاداری (Business with password)

---

## 📱 بخش اسکن QR و امتیاز

### 5. `POST /api/rewards/scan-products/` - اسکن QR با محصولات

#### 📝 فیلدهای Request:

| فیلد | نوع | Required | توضیحات |
|------|-----|----------|---------|
| `business_id` | integer | ✅ بله | شناسه کسب‌وکار |
| `product_ids` | array[integer] | ✅ بله | آرایه شناسه محصولات (non-empty) |
| `user_id` | string | ⚠️ شرطی | اگر کاربر لاگین نکرده باشد، required است (شماره تلفن کاربر) |

#### 🔍 منطق کد (QRProductScanView.post):

```python
# 1. بررسی business_id و product_ids
# 2. اگر کاربر لاگین کرده: user = request.user
# 3. اگر کاربر لاگین نکرده:
#    - اگر user_id (شماره تلفن) داده نشده -> Error 400
#    - بررسی می‌کند آیا Profile با این شماره تلفن وجود دارد
#    - اگر وجود دارد: user = profile.user
#    - اگر وجود ندارد: User و Profile جدید ایجاد می‌کند
#       - username: "user_{phone}_{business_id}"
#       - email: "{username}@temp.local"
#       - password: None
#       - profile.phone = user_id (شماره تلفن)
#       - profile.role = CUSTOMER
# 4. Customer ایجاد/بازیابی می‌شود
# 5. Products از business_id و product_ids دریافت می‌شوند
# 6. total_points = sum(product.points_reward)
# 7. Wallet ایجاد/بازیابی می‌شود
# 8. PointsTransaction ایجاد می‌شود (points = total_points)
# 9. current_balance محاسبه می‌شود
```

#### 📊 فیلدهای Response:

```json
{
  "success": true,
  "is_new_user": boolean,
  "user_id": integer,
  "customer_id": integer,
  "business_id": integer,
  "business_name": string,
  "products": [
    {
      "id": integer,
      "title": string,
      "points_reward": integer
    }
  ],
  "total_points_awarded": integer,
  "current_balance": integer,
  "transaction_id": integer,
  "wallet_id": integer
}
```

#### 🗄️ ساختار دیتابیس:

**Customer Model:**
- `id`: AutoField (Primary Key)
- `user`: OneToOneField(User)
- `phone`: CharField(max_length=32, blank=True)

**Product Model:**
- `id`: AutoField (Primary Key)
- `business`: ForeignKey(Business)
- `title`: CharField(max_length=200)
- `price_cents`: PositiveIntegerField(default=0)
- `active`: BooleanField(default=True)
- `points_reward`: PositiveIntegerField(default=0)
- `image`: ImageField(upload_to="products/", blank=True, null=True)

**Wallet Model:**
- `id`: AutoField (Primary Key)
- `customer`: ForeignKey(Customer, related_name="wallets")
- `business`: ForeignKey(Business, related_name="wallets")
- `points_balance`: PositiveIntegerField(default=0)
- `reward_point_cost`: PositiveIntegerField(default=100)
- `updated_at`: DateTimeField(auto_now=True)
- **unique_together**: ("customer", "business")

**PointsTransaction Model:**
- `id`: AutoField (Primary Key)
- `wallet`: ForeignKey(Wallet, related_name="points_transactions")
- `campaign`: ForeignKey(Campaign, null=True, blank=True)
- `points`: IntegerField() (positive = earn, negative = redeem)
- `created_at`: DateTimeField(auto_now_add=True)
- `note`: CharField(max_length=200, blank=True)

---

### 6. `GET /api/rewards/balance/` - موجودی امتیاز

#### 📝 Headers:

| Header | نوع | Required |
|--------|-----|----------|
| `Authorization` | string | ✅ بله |

#### 📊 فیلدهای Response:

```json
{
  "wallets": [
    {
      "business_id": integer,
      "business_name": string,
      "balance": integer  // sum of all points_transactions.points
    }
  ]
}
```

#### 🔍 منطق کد:

```python
# 1. Customer ایجاد/بازیابی می‌شود
# 2. تمام Walletهای این customer دریافت می‌شوند
# 3. برای هر wallet:
#    - balance = sum(wallet.points_transactions.points)
#    - نتیجه اضافه می‌شود
```

---

### 7. `GET /api/rewards/history/` - تاریخچه امتیازها

#### 📝 Headers:

| Header | نوع | Required |
|--------|-----|----------|
| `Authorization` | string | ✅ بله |

#### 📝 Query Parameters:

| پارامتر | نوع | Required | توضیحات |
|---------|-----|----------|---------|
| `business_id` | integer | ❌ خیر | فیلتر بر اساس کسب‌وکار |
| `page` | integer | ❌ خیر | شماره صفحه |
| `page_size` | integer | ❌ خیر | تعداد آیتم در صفحه |

#### 📊 فیلدهای Response (PointsTransactionSerializer):

```json
{
  "results": [
    {
      "id": integer,
      "wallet_id": integer,
      "campaign_id": integer (nullable),
      "business_id": integer (nullable),
      "business_name": string (nullable),
      "points": integer,  // positive = earn, negative = redeem
      "created_at": datetime,
      "note": string
    }
  ],
  "count": integer
}
```

---

### 8. `POST /api/rewards/redeem/` - استفاده از امتیاز

#### 📝 فیلدهای Request:

| فیلد | نوع | Required | توضیحات |
|------|-----|----------|---------|
| `business_id` | integer | ✅ بله | شناسه کسب‌وکار |
| `amount` | integer | ✅ بله | تعداد امتیاز (باید > 0) |

#### 🔍 منطق کد (RedeemPointsView.post):

```python
# 1. business_id و amount بررسی می‌شوند
# 2. اگر amount <= 0 -> Error 400
# 3. Business دریافت می‌شود
# 4. Customer ایجاد/بازیابی می‌شود
# 5. Wallet دریافت می‌شود (select_for_update)
# 6. current_balance = sum(wallet.points_transactions.points)
# 7. اگر current_balance < amount -> Error 400 "insufficient points"
# 8. PointsTransaction ایجاد می‌شود (points = -amount, note = "redeem")
```

#### 📊 فیلدهای Response:

**✅ 200 OK:**
```json
{
  "redeemed": integer
}
```

**❌ 400 Bad Request:**
```json
{
  "detail": "invalid amount"  // یا "insufficient points"
}
```

---

## 📝 بخش نظرات

### 9. `POST /api/reviews/` - ثبت نظر

#### 📝 فیلدهای Request:

| فیلد | نوع | Required | توضیحات |
|------|-----|----------|---------|
| `business_id` | integer | ✅ بله | شناسه کسب‌وکار |
| `rating` | integer | ✅ بله | امتیاز (1-5) |
| `comment` | string | ❌ خیر | متن نظر |

#### 🔍 منطق کد (ReviewSerializer.create):

```python
# 1. business_id از validated_data استخراج می‌شود
# 2. Business با این ID دریافت می‌شود
# 3. اگر Business وجود نداشته باشد -> Error
# 4. validated_data["business"] = business
# 5. customer از request.user گرفته می‌شود
# 6. Review ایجاد می‌شود
```

#### 📊 فیلدهای Response (ReviewSerializer):

```json
{
  "id": integer,
  "business": Business object,
  "customer": Customer object,
  "rating": integer (1-5),
  "comment": string,
  "created_at": datetime
}
```

#### 🗄️ ساختار دیتابیس:

**Review Model:**
- `id`: AutoField (Primary Key)
- `business`: ForeignKey(Business, related_name="reviews")
- `customer`: ForeignKey(Customer, related_name="reviews")
- `rating`: PositiveSmallIntegerField()
- `comment`: TextField(blank=True)
- `created_at`: DateTimeField(auto_now_add=True)
- **unique_together**: ("business", "customer") - هر مشتری فقط یک نظر می‌تواند برای هر کسب‌وکار بگذارد

---

## 💳 بخش پرداخت

### 10. `POST /api/payments/initiate/` - شروع پرداخت

#### 📝 فیلدهای Request:

| فیلد | نوع | Required | توضیحات |
|------|-----|----------|---------|
| `business_id` | integer | ✅ بله | شناسه کسب‌وکار |
| `amount_cents` | integer | ✅ بله | مبلغ به ریال |
| `currency` | string | ❌ خیر | واحد پول (default: "USD") |

#### 🔍 منطق کد:

```python
# 1. Order ایجاد می‌شود:
#    - user = request.user
#    - business = Business.objects.get(id=business_id)
#    - amount_cents = request.data.get("amount_cents")
#    - currency = request.data.get("currency", "USD")
#    - status = "pending"
# 2. PaymentIntent با Stripe ایجاد می‌شود
# 3. Order.external_id = payment_intent.id
# 4. Order.status بر اساس payment_intent
```

#### 📊 فیلدهای Response:

```json
{
  "order_id": integer,
  "payment_intent_id": string,
  "client_secret": string,
  "amount_cents": integer
}
```

#### 🗄️ ساختار دیتابیس:

**Order Model:**
- `id`: AutoField (Primary Key)
- `user`: ForeignKey(User, null=True, blank=True)
- `business`: ForeignKey(Business, related_name="orders")
- `amount_cents`: PositiveIntegerField()
- `currency`: CharField(max_length=8, default="USD")
- `status`: CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
  - Choices: "pending", "paid", "failed"
- `external_id`: CharField(max_length=128, blank=True)  // Stripe payment intent ID
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)

---

## 🔔 بخش نوتیفیکیشن

### 11. `POST /api/notifications/register-device/` - ثبت دستگاه

#### 📝 فیلدهای Request:

| فیلد | نوع | Required | توضیحات |
|------|-----|----------|---------|
| `token` | string | ✅ بله | FCM device token |
| `platform` | string | ❌ خیر | "ios" یا "android" |

#### 🗄️ ساختار دیتابیس (اگر وجود دارد):

باید Device model داشته باشد که شامل:
- `user`: ForeignKey(User)
- `token`: CharField (FCM token)
- `platform`: CharField (choices: "ios", "android")
- `created_at`: DateTimeField
- `updated_at`: DateTimeField

---

## 📋 خلاصه فیلدهای اصلی هر Model

### User (Django built-in):
- `id`, `username`, `password`, `email`, `first_name`, `last_name`, `date_joined`, `is_active`

### Profile:
- `id`, `user`, `role`, `phone`, `business_name`, `is_active`, `last_login_ip`, `created_at`, `updated_at`, `business_type`, `business_address`, `business_phone`, `total_logins`, `last_activity`

### Customer:
- `id`, `user`, `phone`

### Business (loyalty):
- `id`, `owner`, `name`, `description`, `address`, `website`, `phone`, `password`, `free_reward_threshold`, `created_at`

### Product:
- `id`, `business`, `title`, `price_cents`, `active`, `points_reward`, `image`

### Wallet:
- `id`, `customer`, `business`, `points_balance`, `reward_point_cost`, `updated_at`
- **unique_together**: (customer, business)

### PointsTransaction:
- `id`, `wallet`, `campaign`, `points`, `created_at`, `note`

### Review:
- `id`, `business`, `customer`, `rating`, `comment`, `created_at`
- **unique_together**: (business, customer)

### Order:
- `id`, `user`, `business`, `amount_cents`, `currency`, `status`, `external_id`, `created_at`, `updated_at`

### Campaign:
- `id`, `business`, `name`, `description`, `start_at`, `end_at`, `is_active`, `points_per_scan`, `daily_limit`, `created_at`

---

## 🔄 نکات مهم تغییرات

### اگر می‌خواهید فیلدی اضافه کنید:

1. **در Model**: فیلد را به model اضافه کنید
2. **Migration**: `python manage.py makemigrations` و `migrate`
3. **در Serializer**: فیلد را به `fields` اضافه کنید
4. **در View**: اگر منطق خاصی نیاز است، اضافه کنید
5. **در API Documentation**: این فایل را به‌روز کنید

### مثال: اضافه کردن فیلد `birth_date` به Profile

```python
# 1. accounts/models.py
class Profile(models.Model):
    # ... existing fields ...
    birth_date = models.DateField(null=True, blank=True)

# 2. Migration
python manage.py makemigrations
python manage.py migrate

# 3. accounts/serializers.py
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            # ... existing fields ...
            "birth_date"
        ]

# 4. API documentation را به‌روز کنید
```

---

**نکته**: این فایل باید همیشه با کد همگام باشد. اگر تغییری در مدل‌ها، serializerها یا viewها دادید، این فایل را به‌روز کنید.

