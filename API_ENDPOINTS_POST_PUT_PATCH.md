# 📱 راهنمای کامل API برای اپلیکیشن موبایل

این مستندات برای استفاده در اپلیکیشن React Native طراحی شده است. هر API شامل نام متد، نوع درخواست، ساختار داده‌ها و منطق کسب‌وکار است.

---

## 🔐 بخش احراز هویت و ثبت نام

### 1. `sendNumber` - ارسال شماره تلفن برای بررسی

**متد**: `POST`  
**آدرس**: `/api/accounts/check-phone/`  
**احراز هویت**: ندارد

#### درخواست (Request Body):
```json
{
  "number": "09123456789"
}
```

**ساختار داده:**
- `number`: `string` (required) - شماره تلفن به صورت رشته

#### پاسخ‌ها:

**✅ 201 Created** - کاربر قبلاً ثبت نام کرده است  
```json
{
  "user_exists": true,
  "message": "کاربر موجود است، لطفاً رمز عبور را وارد کنید"
}
```
**منطق کسب‌وکار**: اگر `201` دریافت کردی، کاربر را به صفحه وارد کردن رمز عبور (`LoginScreen`) هدایت کن.

**✅ 200 OK** - کاربر جدید است  
```json
{
  "user_exists": false,
  "message": "کاربر جدید است، لطفاً ثبت نام کنید"
}
```
**منطق کسب‌وکار**: اگر `200` دریافت کردی، کاربر را به صفحه ثبت نام (`RegisterScreen`) هدایت کن.

**❌ 404 Not Found** - شماره تلفن نامعتبر است  
```json
{
  "error": "شماره تلفن نامعتبر است"
}
```

**❌ 400 Bad Request** - شماره تلفن ارسال نشده  
```json
{
  "error": "شماره تلفن الزامی است"
}
```

---

### 2. `loginWithPassword` - ورود با شماره تلفن و رمز عبور

**متد**: `POST`  
**آدرس**: `/api/accounts/login/`  
**احراز هویت**: ندارد

#### درخواست (Request Body):
```json
{
  "phone": "09123456789",
  "password": "myPassword123"
}
```

**ساختار داده:**
- `phone`: `string` (required) - شماره تلفن
- `password`: `string` (required) - رمز عبور

#### پاسخ‌ها:

**✅ 200 OK** - ورود موفق  
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "user_09123456789",
    "phone": "09123456789"
  }
}
```
**منطق کسب‌وکار**: 
- `access` و `refresh` را در AsyncStorage یا secure storage ذخیره کن
- در هدر درخواست‌های بعدی از `Authorization: Bearer <access>` استفاده کن
- کاربر را به صفحه اصلی اپلیکیشن (`HomeScreen`) هدایت کن

**❌ 401 Unauthorized** - رمز عبور اشتباه است  
```json
{
  "error": "شماره تلفن یا رمز عبور اشتباه است"
}
```

**❌ 404 Not Found** - کاربر پیدا نشد  
```json
{
  "error": "کاربر با این شماره تلفن پیدا نشد"
}
```

---

### 3. `getInterests` - دریافت لیست علاقه‌مندی‌ها (قبل از ثبت نام)

**متد**: `GET`  
**آدرس**: `/api/accounts/interests/`  
**احراز هویت**: ندارد

#### درخواست:
بدون بدنه - فقط GET request

#### پاسخ‌ها:

**✅ 200 OK** - لیست علاقه‌مندی‌ها  
```json
{
  "interests": [
    {
      "id": 1,
      "name": "رستوران",
      "icon": "restaurant"
    },
    {
      "id": 2,
      "name": "کافی‌شاپ",
      "icon": "cafe"
    },
    {
      "id": 3,
      "name": "فروشگاه",
      "icon": "store"
    }
  ]
}
```
**منطق کسب‌وکار**: این لیست را در صفحه ثبت نام نمایش بده تا کاربر بتواند علاقه‌مندی‌هایش را انتخاب کند.

---

### 4. `register` - ثبت نام کاربر جدید

**متد**: `POST`  
**آدرس**: `/api/accounts/register/`  
**احراز هویت**: ندارد

#### درخواست (Request Body):
```json
{
  "phone": "09123456789",
  "password": "myPassword123",
  "password_confirm": "myPassword123",
  "first_name": "علی",
  "last_name": "احمدی",
  "email": "ali@example.com",
  "interests": [1, 2, 3]
}
```

**ساختار داده:**
- `phone`: `string` (required) - شماره تلفن
- `password`: `string` (required) - رمز عبور
- `password_confirm`: `string` (required) - تکرار رمز عبور
- `first_name`: `string` (optional) - نام
- `last_name`: `string` (optional) - نام خانوادگی
- `email`: `string` (optional) - ایمیل
- `interests`: `array<number>` (optional) - آرایه شناسه‌های علاقه‌مندی‌ها

#### پاسخ‌ها:

**✅ 201 Created** - ثبت نام موفق  
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 5,
    "username": "user_09123456789",
    "phone": "09123456789",
    "first_name": "علی",
    "last_name": "احمدی"
  }
}
```
**منطق کسب‌وکار**: 
- `access` و `refresh` را در AsyncStorage ذخیره کن
- در هدر درخواست‌های بعدی از `Authorization: Bearer <access>` استفاده کن
- کاربر را به صفحه اصلی اپلیکیشن (`HomeScreen`) هدایت کن
- دفعه بعدی که اپ باز شد، در صفحه Splash توکن را بررسی کن و اگر معتبر بود، کاربر را مستقیماً به صفحه اصلی ببر

**❌ 400 Bad Request** - خطا در ثبت نام  
```json
{
  "error": "رمز عبور و تکرار آن مطابقت ندارند"
}
```
یا
```json
{
  "error": "این شماره تلفن قبلاً ثبت شده است"
}
```

---

### 5. `checkToken` - بررسی معتبر بودن توکن (در صفحه Splash)

**متد**: `GET`  
**آدرس**: `/api/accounts/me/`  
**احراز هویت**: نیاز دارد (`Authorization: Bearer <token>`)

#### درخواست Headers:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### پاسخ‌ها:

**✅ 200 OK** - توکن معتبر است  
```json
{
  "user": {
    "id": 1,
    "username": "user_09123456789",
    "phone": "09123456789",
    "first_name": "علی",
    "last_name": "احمدی"
  },
  "profile": {
    "id": 1,
    "role": "customer",
    "phone": "09123456789"
  }
}
```
**منطق کسب‌وکار**: 
- اگر `200` دریافت کردی، توکن معتبر است
- کاربر را به صفحه اصلی (`HomeScreen`) ببر
- دیگر نیازی به صفحه لاگین نیست

**❌ 401 Unauthorized** - توکن نامعتبر یا منقضی شده  
```json
{
  "detail": "Given token not valid for any token type"
}
```
**منطق کسب‌وکار**: 
- اگر `401` دریافت کردی، توکن را از storage پاک کن
- کاربر را به صفحه وارد کردن شماره تلفن (`PhoneNumberScreen`) ببر

---

### 6. `refreshToken` - تازه‌سازی توکن

**متد**: `POST`  
**آدرس**: `/api/accounts/token/refresh/`  
**احراز هویت**: ندارد

#### درخواست (Request Body):
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**ساختار داده:**
- `refresh`: `string` (required) - refresh token

#### پاسخ‌ها:

**✅ 200 OK** - توکن تازه شده  
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
**منطق کسب‌وکار**: 
- `access` و `refresh` جدید را جایگزین توکن‌های قبلی در storage کن
- اگر توکن منقضی شده بود، با این متد می‌توانی بدون نیاز به لاگین دوباره توکن جدید بگیری

**❌ 401 Unauthorized** - refresh token نامعتبر  
```json
{
  "detail": "Token is invalid or expired"
}
```
**منطق کسب‌وکار**: کاربر را به صفحه لاگین ببر

---

## 🏪 بخش کسب‌وکارها و اسلایدر

### 7. `getBusinesses` - دریافت لیست کسب‌وکارها (اسلایدر)

**متد**: `GET`  
**آدرس**: `/api/businesses/`  
**احراز هویت**: ندارد (برای نمایش عمومی)

#### درخواست Query Parameters:
- `type`: `string` (optional) - فیلتر بر اساس نوع کسب‌وکار
- `is_active`: `boolean` (optional) - فقط کسب‌وکارهای فعال

مثال: `/api/businesses/?is_active=true`

#### پاسخ‌ها:

**✅ 200 OK** - لیست کسب‌وکارها  
```json
{
  "results": [
    {
      "id": 1,
      "name": "کافی‌شاپ آلی",
      "description": "بهترین قهوه شهر",
      "business_type": "cafe",
      "address": "تهران، میدان انقلاب",
      "phone": "021-12345678",
      "image": "https://example.com/images/cafe.jpg",
      "is_active": true,
      "rating": 4.5,
      "total_reviews": 120
    },
    {
      "id": 2,
      "name": "رستوران داریوش",
      "description": "غذای ایرانی و فرنگی",
      "business_type": "restaurant",
      "address": "تهران، خیابان ولیعصر",
      "phone": "021-87654321",
      "image": "https://example.com/images/restaurant.jpg",
      "is_active": true,
      "rating": 4.8,
      "total_reviews": 250
    }
  ],
  "count": 2
}
```
**منطق کسب‌وکار**: 
- این لیست را در اسلایدر صفحه اصلی نمایش بده
- کاربر می‌تواند با کلیک روی هر کسب‌وکار به صفحه جزئیات آن برود

---

## 📱 بخش اسکن QR و امتیاز

### 8. `scanQRCode` - اسکن QR کد و دریافت امتیاز

**متد**: `POST`  
**آدرس**: `/api/rewards/scan-products/`  
**احراز هویت**: دارد (اما برای کاربران جدید اختیاری است)

#### درخواست (Request Body):
```json
{
  "business_id": 1,
  "product_ids": [1, 2, 3],
  "phone": "09123456789"
}
```

**ساختار داده:**
- `business_id`: `number` (required) - شناسه کسب‌وکار
- `product_ids`: `array<number>` (required) - آرایه شناسه محصولات انتخاب شده
- `phone`: `string` (optional if authenticated, required if not) - شماره تلفن (برای کاربران جدید)

#### درخواست Headers (اگر لاگین کرده‌ای):
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### پاسخ‌ها:

**✅ 201 Created** - اسکن موفق و امتیاز دریافت شد  
```json
{
  "success": true,
  "is_new_user": false,
  "user_id": 5,
  "customer_id": 3,
  "business_id": 1,
  "business_name": "کافی‌شاپ آلی",
  "products": [
    {
      "id": 1,
      "title": "قهوه اسپرسو",
      "points_reward": 10
    },
    {
      "id": 2,
      "title": "کاپوچینو",
      "points_reward": 15
    }
  ],
  "total_points_awarded": 25,
  "current_balance": 45,
  "transaction_id": 123,
  "wallet_id": 8
}
```
**منطق کسب‌وکار**: 
- اگر `is_new_user: true` بود، حساب کاربری جدید برای شماره تلفن ایجاد شده
- امتیاز به حساب کاربر اضافه شده
- `transaction_id` را در دیتابیس محلی ذخیره کن
- موجودی فعلی (`current_balance`) را نمایش بده

**❌ 400 Bad Request** - خطا در درخواست  
```json
{
  "error": "business_id is required"
}
```
یا
```json
{
  "error": "Some products not found or not active",
  "found_products": [1, 2]
}
```
یا
```json
{
  "error": "phone is required for new users",
  "requires_registration": true
}
```

**❌ 404 Not Found** - کسب‌وکار پیدا نشد  
```json
{
  "error": "Business not found"
}
```

---

### 9. `getMyBalance` - دریافت موجودی امتیاز کاربر

**متد**: `GET`  
**آدرس**: `/api/rewards/balance/`  
**احراز هویت**: نیاز دارد (`Authorization: Bearer <token>`)

#### درخواست Headers:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### پاسخ‌ها:

**✅ 200 OK** - موجودی امتیاز  
```json
{
  "wallets": [
    {
      "business_id": 1,
      "business_name": "کافی‌شاپ آلی",
      "balance": 45
    },
    {
      "business_id": 2,
      "business_name": "رستوران داریوش",
      "balance": 120
    }
  ]
}
```
**منطق کسب‌وکار**: 
- موجودی امتیاز کاربر را برای هر کسب‌وکار نشان می‌دهد
- این اطلاعات را در صفحه پروفایل یا داشبورد نمایش بده

---

### 10. `getPointsHistory` - دریافت تاریخچه امتیازها

**متد**: `GET`  
**آدرس**: `/api/rewards/history/`  
**احراز هویت**: نیاز دارد (`Authorization: Bearer <token>`)

#### درخواست Query Parameters:
- `business_id`: `number` (optional) - فیلتر بر اساس کسب‌وکار
- `page`: `number` (optional) - شماره صفحه
- `page_size`: `number` (optional) - تعداد آیتم در هر صفحه

#### پاسخ‌ها:

**✅ 200 OK** - تاریخچه امتیازها  
```json
{
  "results": [
    {
      "id": 1,
      "points": 10,
      "note": "scan",
      "created_at": "2025-01-11T12:00:00Z",
      "business": {
        "id": 1,
        "name": "کافی‌شاپ آلی"
      }
    },
    {
      "id": 2,
      "points": -5,
      "note": "redeem",
      "created_at": "2025-01-10T10:00:00Z",
      "business": {
        "id": 1,
        "name": "کافی‌شاپ آلی"
      }
    }
  ],
  "count": 2
}
```
**منطق کسب‌وکار**: 
- تاریخچه تراکنش‌های امتیاز را نشان می‌دهد
- مثبت = دریافت امتیاز (اسکن)
- منفی = استفاده از امتیاز (redeem)

---

### 11. `redeemPoints` - استفاده از امتیاز (دریافت پاداش)

**متد**: `POST`  
**آدرس**: `/api/rewards/redeem/`  
**احراز هویت**: نیاز دارد (`Authorization: Bearer <token>`)

#### درخواست (Request Body):
```json
{
  "business_id": 1,
  "amount": 10
}
```

**ساختار داده:**
- `business_id`: `number` (required) - شناسه کسب‌وکار
- `amount`: `number` (required) - تعداد امتیاز مورد استفاده

#### پاسخ‌ها:

**✅ 200 OK** - استفاده از امتیاز موفق  
```json
{
  "redeemed": 10,
  "new_balance": 35
}
```
**منطق کسب‌وکار**: 
- امتیاز از حساب کاربر کسر شده
- موجودی جدید را به کاربر نشان بده

**❌ 400 Bad Request** - موجودی کافی نیست  
```json
{
  "detail": "insufficient points"
}
```

---

## 📝 بخش نظرات

### 12. `submitReview` - ثبت نظر برای کسب‌وکار

**متد**: `POST`  
**آدرس**: `/api/reviews/`  
**احراز هویت**: نیاز دارد (`Authorization: Bearer <token>`)

#### درخواست (Request Body):
```json
{
  "business_id": 1,
  "rating": 5,
  "comment": "عالی بود!"
}
```

**ساختار داده:**
- `business_id`: `number` (required) - شناسه کسب‌وکار
- `rating`: `number` (required, 1-5) - امتیاز (۱ تا ۵)
- `comment`: `string` (optional) - متن نظر

#### پاسخ‌ها:

**✅ 201 Created** - نظر ثبت شد  
```json
{
  "id": 10,
  "business_id": 1,
  "rating": 5,
  "comment": "عالی بود!",
  "created_at": "2025-01-11T12:00:00Z"
}
```

**❌ 400 Bad Request** - خطا در ثبت نظر  
```json
{
  "error": "rating must be between 1 and 5"
}
```

---

## 💳 بخش پرداخت

### 13. `initiatePayment` - شروع پرداخت

**متد**: `POST`  
**آدرس**: `/api/payments/initiate/`  
**احراز هویت**: نیاز دارد (`Authorization: Bearer <token>`)

#### درخواست (Request Body):
```json
{
  "business_id": 1,
  "amount_cents": 50000,
  "currency": "IRR"
}
```

**ساختار داده:**
- `business_id`: `number` (required) - شناسه کسب‌وکار
- `amount_cents`: `number` (required) - مبلغ به ریال (50000 = 500 هزار تومان)
- `currency`: `string` (optional, default: "IRR") - واحد پول

#### پاسخ‌ها:

**✅ 200 OK** - پرداخت آماده است  
```json
{
  "order_id": 5,
  "payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_abc",
  "amount_cents": 50000
}
```
**منطق کسب‌وکار**: 
- `client_secret` را به Stripe SDK بده
- پرداخت را شروع کن

**❌ 400 Bad Request** - خطا در شروع پرداخت  
```json
{
  "error": "Invalid amount"
}
```

---

## 🔔 بخش نوتیفیکیشن

### 14. `registerDevice` - ثبت دستگاه برای Push Notification

**متد**: `POST`  
**آدرس**: `/api/notifications/register-device/`  
**احراز هویت**: نیاز دارد (`Authorization: Bearer <token>`)

#### درخواست (Request Body):
```json
{
  "token": "fcm_device_token_here",
  "platform": "ios"
}
```

**ساختار داده:**
- `token`: `string` (required) - FCM device token
- `platform`: `string` (optional, "ios" | "android") - پلتفرم

#### پاسخ‌ها:

**✅ 201 Created** - دستگاه ثبت شد  
```json
{
  "success": true,
  "device_id": 1
}
```

---

## 🔑 نکات مهم

### ذخیره توکن (Token Storage):
```javascript
// بعد از لاگین یا ثبت نام موفق:
await AsyncStorage.setItem('access_token', response.data.access);
await AsyncStorage.setItem('refresh_token', response.data.refresh);

// استفاده در درخواست‌ها:
const token = await AsyncStorage.getItem('access_token');
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### صفحه Splash Flow:
```javascript
// 1. بررسی توکن در storage
const token = await AsyncStorage.getItem('access_token');

// 2. اگر توکن وجود دارد، بررسی معتبر بودن
if (token) {
  try {
    const response = await axios.get('/api/accounts/me/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    // توکن معتبر است -> برو به HomeScreen
    navigate('Home');
  } catch (error) {
    // توکن نامعتبر است -> پاک کن و برو به PhoneNumberScreen
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
    navigate('PhoneNumber');
  }
} else {
  // توکن وجود ندارد -> برو به PhoneNumberScreen
  navigate('PhoneNumber');
}
```

### مدیریت خطاهای 401 (Unauthorized):
```javascript
// در interceptor axios:
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // تلاش برای refresh token
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const refreshResponse = await axios.post('/api/accounts/token/refresh/', {
            refresh: refreshToken
          });
          // ذخیره توکن جدید
          await AsyncStorage.setItem('access_token', refreshResponse.data.access);
          await AsyncStorage.setItem('refresh_token', refreshResponse.data.refresh);
          // تکرار درخواست اصلی
          error.config.headers['Authorization'] = `Bearer ${refreshResponse.data.access}`;
          return axios.request(error.config);
        } catch (refreshError) {
          // refresh token هم نامعتبر است -> برو به لاگین
          await AsyncStorage.removeItem('access_token');
          await AsyncStorage.removeItem('refresh_token');
          navigate('PhoneNumber');
        }
      } else {
        // refresh token وجود ندارد -> برو به لاگین
        navigate('PhoneNumber');
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 📊 خلاصه Flow کامل اپلیکیشن

### سناریو 1: کاربر جدید
1. اپ باز می‌شود → `SplashScreen`
2. توکن وجود ندارد → `PhoneNumberScreen`
3. شماره تلفن وارد می‌شود → `sendNumber` → پاسخ `200` (کاربر جدید)
4. هدایت به → `RegisterScreen`
5. قبل از ثبت نام → `getInterests` برای دریافت لیست علاقه‌مندی‌ها
6. فرم ثبت نام پر می‌شود → `register` → دریافت توکن
7. توکن ذخیره می‌شود → هدایت به → `HomeScreen`

### سناریو 2: کاربر موجود (لاگین نکرده)
1. اپ باز می‌شود → `SplashScreen`
2. توکن وجود ندارد → `PhoneNumberScreen`
3. شماره تلفن وارد می‌شود → `sendNumber` → پاسخ `201` (کاربر موجود)
4. هدایت به → `LoginScreen` (رمز عبور)
5. رمز عبور وارد می‌شود → `loginWithPassword` → دریافت توکن
6. توکن ذخیره می‌شود → هدایت به → `HomeScreen`

### سناریو 3: کاربر لاگین کرده (باز شدن اپ)
1. اپ باز می‌شود → `SplashScreen`
2. توکن از storage خوانده می‌شود → `checkToken` → پاسخ `200` (معتبر)
3. مستقیماً → `HomeScreen` (بدون نیاز به لاگین)

### سناریو 4: اسکن QR (کاربر لاگین کرده)
1. QR اسکن می‌شود → `scanQRCode` (با توکن در header)
2. امتیاز دریافت می‌شود → نمایش موفقیت → به‌روزرسانی موجودی

### سناریو 5: اسکن QR (کاربر لاگین نکرده)
1. QR اسکن می‌شود → `scanQRCode` (بدون توکن، با شماره تلفن)
2. اگر کاربر جدید بود، حساب ساخته می‌شود
3. امتیاز دریافت می‌شود → نمایش موفقیت

---

## ✅ چک‌لیست پیاده‌سازی

- [ ] `sendNumber` - بررسی شماره تلفن
- [ ] `loginWithPassword` - ورود با رمز عبور
- [ ] `getInterests` - دریافت علاقه‌مندی‌ها
- [ ] `register` - ثبت نام
- [ ] `checkToken` - بررسی توکن در Splash
- [ ] `refreshToken` - تازه‌سازی توکن
- [ ] `getBusinesses` - لیست کسب‌وکارها
- [ ] `scanQRCode` - اسکن QR
- [ ] `getMyBalance` - موجودی امتیاز
- [ ] `getPointsHistory` - تاریخچه
- [ ] `redeemPoints` - استفاده از امتیاز
- [ ] `submitReview` - ثبت نظر
- [ ] `initiatePayment` - پرداخت
- [ ] `registerDevice` - ثبت دستگاه

---

**نکته**: همه API های POST/PUT/PATCH که نیاز به احراز هویت دارند باید `Authorization: Bearer <token>` در header ارسال کنند.
