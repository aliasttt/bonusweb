# 📱 راهنمای کامل API برای React Native

این راهنما تمام APIهای مورد نیاز برای توسعه اپلیکیشن React Native را شامل می‌شود.

**Base URL**: `http://your-server.com/api`

---

## 🔑 تنظیمات اولیه

### نصب Axios (اگر ندارید):
```bash
npm install axios
```

### ساختار API Service:
```javascript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://your-server.com/api';

// ساخت instance از axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor برای اضافه کردن token به header
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor برای مدیریت خطاهای 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // تلاش برای refresh token
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/accounts/token/refresh/`, {
            refresh: refreshToken
          });
          await AsyncStorage.setItem('access_token', response.data.access);
          await AsyncStorage.setItem('refresh_token', response.data.refresh);
          // تکرار درخواست اصلی
          error.config.headers.Authorization = `Bearer ${response.data.access}`;
          return axios.request(error.config);
        } catch (refreshError) {
          // refresh token هم نامعتبر است -> برو به لاگین
          await AsyncStorage.removeItem('access_token');
          await AsyncStorage.removeItem('refresh_token');
          // navigate to login
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 🔐 بخش 1: احراز هویت و ثبت نام

### 1.1 ثبت نام کاربر جدید

**Endpoint**: `POST /api/accounts/register/`  
**احراز هویت**: ندارد

#### Request Body:
```json
{
  "username": "user_09123456789",
  "password": "myPassword123",
  "password_confirm": "myPassword123",
  "email": "user@example.com",
  "first_name": "علی",
  "last_name": "احمدی",
  "phone": "09123456789"
}
```

#### فیلدها:
| فیلد | نوع | الزامی | توضیحات |
|------|-----|--------|---------|
| `username` | string | ✅ | نام کاربری (unique) |
| `password` | string | ✅ | رمز عبور |
| `password_confirm` | string | ✅ | تکرار رمز عبور (باید با password مطابقت داشته باشد) |
| `email` | string | ❌ | ایمیل (اختیاری) |
| `first_name` | string | ❌ | نام (اختیاری) |
| `last_name` | string | ❌ | نام خانوادگی (اختیاری) |
| `phone` | string | ❌ | شماره تلفن (اختیاری) |

#### Response (201 Created):
```json
{
  "user": {
    "id": 5,
    "username": "user_09123456789",
    "first_name": "علی",
    "last_name": "احمدی",
    "email": "user@example.com",
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

**⚠️ نکته مهم**: این endpoint توکن برنمی‌گرداند. بعد از ثبت نام باید لاگین کنید تا token دریافت کنید.

#### مثال کد:
```javascript
async function register(userData) {
  try {
    const response = await api.post('/accounts/register/', {
      username: userData.username,
      password: userData.password,
      password_confirm: userData.passwordConfirm,
      email: userData.email || '',
      first_name: userData.firstName || '',
      last_name: userData.lastName || '',
      phone: userData.phone || ''
    });
    
    // بعد از ثبت نام موفق، باید لاگین کنید
    const loginResponse = await api.post('/accounts/token/', {
      username: userData.username,
      password: userData.password
    });
    
    // ذخیره token
    await AsyncStorage.setItem('access_token', loginResponse.data.access);
    await AsyncStorage.setItem('refresh_token', loginResponse.data.refresh);
    
    return { user: response.data.user, profile: response.data.profile };
  } catch (error) {
    console.error('Registration error:', error.response?.data);
    throw error;
  }
}
```

---

### 1.2 ورود (لاگین) با Username و Password

**Endpoint**: `POST /api/accounts/token/`  
**احراز هویت**: ندارد

#### Request Body:
```json
{
  "username": "user_09123456789",
  "password": "myPassword123"
}
```

#### Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### مثال کد:
```javascript
async function login(username, password) {
  try {
    const response = await api.post('/accounts/token/', {
      username: username,
      password: password
    });
    
    // ذخیره token در AsyncStorage
    await AsyncStorage.setItem('access_token', response.data.access);
    await AsyncStorage.setItem('refresh_token', response.data.refresh);
    
    // دریافت اطلاعات کاربر
    const userResponse = await api.get('/accounts/me/');
    
    return {
      token: response.data.access,
      refreshToken: response.data.refresh,
      user: userResponse.data.user,
      profile: userResponse.data.profile
    };
  } catch (error) {
    console.error('Login error:', error.response?.data);
    throw error;
  }
}
```

---

### 1.3 دریافت اطلاعات کاربر فعلی (بررسی Token)

**Endpoint**: `GET /api/accounts/me/`  
**احراز هویت**: نیاز دارد (`Authorization: Bearer <token>`)

#### Response (200 OK):
```json
{
  "user": {
    "id": 1,
    "username": "user_09123456789",
    "first_name": "علی",
    "last_name": "احمدی",
    "email": "user@example.com",
    "date_joined": "2025-01-11T12:00:00Z",
    "is_active": true
  },
  "profile": {
    "id": 1,
    "role": "customer",
    "phone": "09123456789",
    "business_name": "",
    "is_active": true,
    "last_login_ip": null,
    "created_at": "2025-01-11T12:00:00Z",
    "updated_at": "2025-01-11T12:00:00Z",
    "business_type": "",
    "business_address": "",
    "business_phone": "",
    "total_logins": 0,
    "last_activity": null
  }
}
```

#### استفاده در Splash Screen:
```javascript
async function checkAuth() {
  try {
    const token = await AsyncStorage.getItem('access_token');
    if (!token) {
      return { isAuthenticated: false };
    }
    
    const response = await api.get('/accounts/me/');
    return {
      isAuthenticated: true,
      user: response.data.user,
      profile: response.data.profile
    };
  } catch (error) {
    // Token نامعتبر است
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
    return { isAuthenticated: false };
  }
}
```

---

### 1.4 تازه‌سازی Token (Refresh Token)

**Endpoint**: `POST /api/accounts/token/refresh/`  
**احراز هویت**: ندارد

#### Request Body:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### مثال کد:
```javascript
async function refreshToken() {
  try {
    const refreshToken = await AsyncStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await api.post('/accounts/token/refresh/', {
      refresh: refreshToken
    });
    
    await AsyncStorage.setItem('access_token', response.data.access);
    await AsyncStorage.setItem('refresh_token', response.data.refresh);
    
    return response.data;
  } catch (error) {
    // Refresh token نامعتبر است -> برو به لاگین
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
    throw error;
  }
}
```

---

## 🏪 بخش 2: کسب‌وکارها

### 2.1 دریافت لیست کسب‌وکارها

**Endpoint**: `GET /api/businesses/`  
**احراز هویت**: ندارد

#### Query Parameters (اختیاری):
- `is_active`: boolean - فقط کسب‌وکارهای فعال
- `type`: string - فیلتر بر اساس نوع کسب‌وکار

#### Response (200 OK):
```json
[
  {
    "id": 1,
    "name": "کافی‌شاپ آلی",
    "description": "بهترین قهوه شهر",
    "address": "تهران، میدان انقلاب",
    "website": "https://example.com",
    "phone": "021-12345678",
    "free_reward_threshold": 10,
    "created_at": "2025-01-01T10:00:00Z"
  },
  {
    "id": 2,
    "name": "رستوران داریوش",
    "description": "غذای ایرانی و فرنگی",
    "address": "تهران، خیابان ولیعصر",
    "website": "",
    "phone": "021-87654321",
    "free_reward_threshold": 10,
    "created_at": "2025-01-01T11:00:00Z"
  }
]
```

#### مثال کد:
```javascript
async function getBusinesses(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.is_active !== undefined) {
      params.append('is_active', filters.is_active);
    }
    if (filters.type) {
      params.append('type', filters.type);
    }
    
    const response = await api.get(`/businesses/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Get businesses error:', error.response?.data);
    throw error;
  }
}
```

---

### 2.2 دریافت لیست محصولات

**Endpoint**: `GET /api/products/`  
**احراز هویت**: ندارد

#### Query Parameters (اختیاری):
- `business_id`: integer - فیلتر بر اساس کسب‌وکار
- `active`: boolean - فقط محصولات فعال

#### Response (200 OK):
```json
[
  {
    "id": 1,
    "business": 1,
    "title": "قهوه اسپرسو",
    "price_cents": 50000,
    "active": true,
    "points_reward": 10,
    "image": "http://server.com/media/products/espresso.jpg"
  },
  {
    "id": 2,
    "business": 1,
    "title": "کاپوچینو",
    "price_cents": 60000,
    "active": true,
    "points_reward": 15,
    "image": "http://server.com/media/products/cappuccino.jpg"
  }
]
```

#### مثال کد:
```javascript
async function getProducts(businessId = null) {
  try {
    const params = new URLSearchParams();
    if (businessId) {
      params.append('business_id', businessId);
    }
    params.append('active', 'true');
    
    const response = await api.get(`/products/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Get products error:', error.response?.data);
    throw error;
  }
}
```

---

## 📱 بخش 3: اسکن QR و امتیاز

### 3.1 اسکن QR با محصولات (برای React Native)

**Endpoint**: `POST /api/rewards/scan-products/`  
**احراز هویت**: اختیاری (اگر لاگین کرده‌ای، نیازی به phone نیست)

#### Request Body:
```json
{
  "business_id": 1,
  "product_ids": [1, 2, 3],
  "phone": "09123456789"
}
```

#### فیلدها:
| فیلد | نوع | الزامی | توضیحات |
|------|-----|--------|---------|
| `business_id` | integer | ✅ | شناسه کسب‌وکار |
| `product_ids` | array[integer] | ✅ | آرایه شناسه محصولات (non-empty) |
| `phone` | string | ⚠️ شرطی | اگر لاگین نکرده‌ای، required است |

#### Response (201 Created):
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

#### مثال کد:
```javascript
async function scanQRCode(businessId, productIds, phone = null) {
  try {
    const requestData = {
      business_id: businessId,
      product_ids: productIds
    };
    
    // اگر لاگین نکرده‌ای، phone را اضافه کن
    if (phone) {
      requestData.phone = phone;
    }
    
    const response = await api.post('/rewards/scan-products/', requestData);
    
    // ذخیره در دیتابیس محلی
    await saveTransactionToLocalDB({
      transaction_id: response.data.transaction_id,
      business_id: response.data.business_id,
      business_name: response.data.business_name,
      total_points: response.data.total_points_awarded,
      current_balance: response.data.current_balance,
      products: response.data.products,
      timestamp: new Date().toISOString()
    });
    
    return response.data;
  } catch (error) {
    console.error('Scan QR error:', error.response?.data);
    throw error;
  }
}

// ذخیره در AsyncStorage یا SQLite
async function saveTransactionToLocalDB(data) {
  try {
    const existing = await AsyncStorage.getItem('transactions');
    const transactions = existing ? JSON.parse(existing) : [];
    transactions.push(data);
    await AsyncStorage.setItem('transactions', JSON.stringify(transactions));
  } catch (error) {
    console.error('Save transaction error:', error);
  }
}
```

#### خطاها:
- **400 Bad Request**: `{"error": "business_id is required"}` - فیلدهای لازم ناقص هستند
- **400 Bad Request**: `{"error": "Some products not found or not active"}` - محصولات پیدا نشدند
- **400 Bad Request**: `{"error": "phone is required for new users", "requires_registration": true}` - کاربر جدید نیاز به phone دارد
- **404 Not Found**: `{"error": "Business not found"}` - کسب‌وکار پیدا نشد

---

### 3.2 دریافت موجودی امتیاز

**Endpoint**: `GET /api/rewards/balance/`  
**احراز هویت**: نیاز دارد

#### Response (200 OK):
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

#### مثال کد:
```javascript
async function getBalance() {
  try {
    const response = await api.get('/rewards/balance/');
    return response.data.wallets;
  } catch (error) {
    console.error('Get balance error:', error.response?.data);
    throw error;
  }
}
```

---

### 3.3 دریافت تاریخچه امتیازها

**Endpoint**: `GET /api/rewards/history/`  
**احراز هویت**: نیاز دارد

#### Query Parameters (اختیاری):
- `business_id`: integer - فیلتر بر اساس کسب‌وکار
- `page`: integer - شماره صفحه
- `page_size`: integer - تعداد آیتم در صفحه

#### Response (200 OK):
```json
{
  "results": [
    {
      "id": 1,
      "wallet_id": 8,
      "campaign_id": null,
      "business_id": 1,
      "business_name": "کافی‌شاپ آلی",
      "points": 10,
      "created_at": "2025-01-11T12:00:00Z",
      "note": "scan"
    },
    {
      "id": 2,
      "wallet_id": 8,
      "campaign_id": null,
      "business_id": 1,
      "business_name": "کافی‌شاپ آلی",
      "points": -5,
      "created_at": "2025-01-10T10:00:00Z",
      "note": "redeem"
    }
  ],
  "count": 2
}
```

**نکته**: `points` مثبت = دریافت امتیاز، منفی = استفاده از امتیاز

#### مثال کد:
```javascript
async function getPointsHistory(businessId = null, page = 1) {
  try {
    const params = new URLSearchParams();
    if (businessId) {
      params.append('business_id', businessId);
    }
    params.append('page', page);
    
    const response = await api.get(`/rewards/history/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Get history error:', error.response?.data);
    throw error;
  }
}
```

---

### 3.4 استفاده از امتیاز (Redeem)

**Endpoint**: `POST /api/rewards/redeem/`  
**احراز هویت**: نیاز دارد

#### Request Body:
```json
{
  "business_id": 1,
  "amount": 10
}
```

#### فیلدها:
| فیلد | نوع | الزامی | توضیحات |
|------|-----|--------|---------|
| `business_id` | integer | ✅ | شناسه کسب‌وکار |
| `amount` | integer | ✅ | تعداد امتیاز مورد استفاده (باید > 0) |

#### Response (200 OK):
```json
{
  "redeemed": 10
}
```

#### مثال کد:
```javascript
async function redeemPoints(businessId, amount) {
  try {
    const response = await api.post('/rewards/redeem/', {
      business_id: businessId,
      amount: amount
    });
    
    return response.data;
  } catch (error) {
    if (error.response?.status === 400) {
      // موجودی کافی نیست یا amount نامعتبر است
      throw new Error(error.response.data.detail || 'Insufficient points');
    }
    console.error('Redeem error:', error.response?.data);
    throw error;
  }
}
```

#### خطاها:
- **400 Bad Request**: `{"detail": "invalid amount"}` - amount باید > 0 باشد
- **400 Bad Request**: `{"detail": "insufficient points"}` - موجودی کافی نیست

---

## 📝 بخش 4: نظرات

### 4.1 ثبت نظر برای کسب‌وکار

**Endpoint**: `POST /api/reviews/`  
**احراز هویت**: نیاز دارد

#### Request Body:
```json
{
  "business_id": 1,
  "rating": 5,
  "comment": "عالی بود!"
}
```

#### فیلدها:
| فیلد | نوع | الزامی | توضیحات |
|------|-----|--------|---------|
| `business_id` | integer | ✅ | شناسه کسب‌وکار |
| `rating` | integer | ✅ | امتیاز (1-5) |
| `comment` | string | ❌ | متن نظر (اختیاری) |

#### Response (201 Created):
```json
{
  "id": 10,
  "business": 1,
  "customer": 3,
  "rating": 5,
  "comment": "عالی بود!",
  "created_at": "2025-01-11T12:00:00Z"
}
```

**نکته**: هر کاربر فقط یک نظر می‌تواند برای هر کسب‌وکار بگذارد.

#### مثال کد:
```javascript
async function submitReview(businessId, rating, comment = '') {
  try {
    const response = await api.post('/reviews/', {
      business_id: businessId,
      rating: rating, // 1-5
      comment: comment
    });
    
    return response.data;
  } catch (error) {
    console.error('Submit review error:', error.response?.data);
    throw error;
  }
}
```

---

### 4.2 دریافت لیست نظرات

**Endpoint**: `GET /api/reviews/`  
**احراز هویت**: ندارد

#### Query Parameters (اختیاری):
- `business_id`: integer - فیلتر بر اساس کسب‌وکار

#### Response (200 OK):
```json
[
  {
    "id": 1,
    "business": 1,
    "customer": 3,
    "rating": 5,
    "comment": "عالی بود!",
    "created_at": "2025-01-11T12:00:00Z"
  }
]
```

#### مثال کد:
```javascript
async function getReviews(businessId = null) {
  try {
    const params = new URLSearchParams();
    if (businessId) {
      params.append('business_id', businessId);
    }
    
    const response = await api.get(`/reviews/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Get reviews error:', error.response?.data);
    throw error;
  }
}
```

---

## 💳 بخش 5: پرداخت

### 5.1 شروع پرداخت

**Endpoint**: `POST /api/payments/initiate/`  
**احراز هویت**: نیاز دارد

#### Request Body:
```json
{
  "business_id": 1,
  "amount_cents": 50000,
  "currency": "IRR"
}
```

#### فیلدها:
| فیلد | نوع | الزامی | توضیحات |
|------|-----|--------|---------|
| `business_id` | integer | ✅ | شناسه کسب‌وکار |
| `amount_cents` | integer | ✅ | مبلغ به ریال (50000 = 500 هزار تومان) |
| `currency` | string | ❌ | واحد پول (default: "USD") |

#### Response (200 OK):
```json
{
  "order_id": 5,
  "payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_abc",
  "amount_cents": 50000
}
```

#### مثال کد:
```javascript
async function initiatePayment(businessId, amountCents, currency = 'IRR') {
  try {
    const response = await api.post('/payments/initiate/', {
      business_id: businessId,
      amount_cents: amountCents,
      currency: currency
    });
    
    // استفاده از Stripe SDK
    // client_secret را به Stripe پرداخت SDK بده
    
    return response.data;
  } catch (error) {
    console.error('Initiate payment error:', error.response?.data);
    throw error;
  }
}
```

---

### 5.2 دریافت لیست سفارشات

**Endpoint**: `GET /api/payments/orders/`  
**احراز هویت**: نیاز دارد

#### Response (200 OK):
```json
[
  {
    "id": 5,
    "user": 1,
    "business": 1,
    "amount_cents": 50000,
    "currency": "IRR",
    "status": "paid",
    "external_id": "pi_1234567890",
    "created_at": "2025-01-11T12:00:00Z",
    "updated_at": "2025-01-11T12:00:00Z"
  }
]
```

#### مثال کد:
```javascript
async function getOrders() {
  try {
    const response = await api.get('/payments/orders/');
    return response.data;
  } catch (error) {
    console.error('Get orders error:', error.response?.data);
    throw error;
  }
}
```

---

## 🔔 بخش 6: نوتیفیکیشن

### 6.1 ثبت دستگاه برای Push Notification

**Endpoint**: `POST /api/notifications/register-device/`  
**احراز هویت**: نیاز دارد

#### Request Body:
```json
{
  "token": "fcm_device_token_here",
  "platform": "ios"
}
```

#### فیلدها:
| فیلد | نوع | الزامی | توضیحات |
|------|-----|--------|---------|
| `token` | string | ✅ | FCM device token |
| `platform` | string | ❌ | "ios" یا "android" |

#### Response (201 Created):
```json
{
  "success": true,
  "device_id": 1
}
```

#### مثال کد:
```javascript
import messaging from '@react-native-firebase/messaging';

async function registerDevice() {
  try {
    // دریافت FCM token
    const token = await messaging().getToken();
    
    const platform = Platform.OS === 'ios' ? 'ios' : 'android';
    
    const response = await api.post('/notifications/register-device/', {
      token: token,
      platform: platform
    });
    
    return response.data;
  } catch (error) {
    console.error('Register device error:', error.response?.data);
    throw error;
  }
}

// فراخوانی بعد از لاگین موفق
async function onLoginSuccess() {
  await registerDevice();
}
```

---

## 🔄 Flow کامل اپلیکیشن

### سناریو 1: کاربر جدید

1. **Splash Screen** → بررسی token در AsyncStorage
2. **اگر token وجود ندارد** → `PhoneNumberScreen`
3. **شماره تلفن وارد می‌شود** → (در حال حاضر endpoint بررسی phone وجود ندارد، باید مستقیماً به register بروید)
4. **Register Screen** → `register()` → سپس `login()`
5. **ذخیره token** → هدایت به `HomeScreen`

### سناریو 2: کاربر موجود (لاگین نکرده)

1. **Splash Screen** → token وجود ندارد
2. **PhoneNumberScreen** → شماره تلفن وارد می‌شود
3. **Login Screen** → `login(username, password)`
4. **ذخیره token** → هدایت به `HomeScreen`

### سناریو 3: کاربر لاگین کرده

1. **Splash Screen** → token از AsyncStorage خوانده می‌شود
2. **بررسی معتبر بودن** → `get('/accounts/me/')`
3. **اگر معتبر است** → مستقیماً `HomeScreen`
4. **اگر نامعتبر است** → `PhoneNumberScreen`

### سناریو 4: اسکن QR (کاربر لاگین کرده)

1. **QR Scanner** → اسکن QR code
2. **استخراج business_id و product_ids** از QR
3. **فراخوانی** → `scanQRCode(businessId, productIds)`
4. **نمایش موفقیت** → به‌روزرسانی موجودی

### سناریو 5: اسکن QR (کاربر لاگین نکرده)

1. **QR Scanner** → اسکن QR code
2. **درخواست شماره تلفن** → از کاربر
3. **فراخوانی** → `scanQRCode(businessId, productIds, phone)`
4. **اگر کاربر جدید بود** → حساب کاربری ایجاد می‌شود
5. **نمایش موفقیت** → به‌روزرسانی موجودی

---

## ⚠️ نکات مهم

### 1. مدیریت Token:
- همیشه token را در `AsyncStorage` یا `SecureStore` ذخیره کنید
- در هر درخواست token را در header `Authorization: Bearer <token>` بفرستید
- اگر خطای 401 دریافت کردید، با refresh token تلاش کنید

### 2. مدیریت خطاها:
- همیشه try-catch استفاده کنید
- خطاهای شبکه را مدیریت کنید
- پیام‌های خطا را به کاربر نمایش دهید

### 3. ذخیره داده‌های محلی:
- تراکنش‌ها را در AsyncStorage یا SQLite ذخیره کنید
- برای offline mode استفاده کنید

### 4. Performance:
- از pagination برای لیست‌های طولانی استفاده کنید
- تصاویر را cache کنید
- درخواست‌های غیرضروری را محدود کنید

---

## 📋 خلاصه Endpoint ها

| Endpoint | Method | Auth | توضیحات |
|----------|--------|------|---------|
| `/accounts/register/` | POST | ❌ | ثبت نام |
| `/accounts/token/` | POST | ❌ | لاگین |
| `/accounts/token/refresh/` | POST | ❌ | تازه‌سازی token |
| `/accounts/me/` | GET | ✅ | اطلاعات کاربر |
| `/businesses/` | GET | ❌ | لیست کسب‌وکارها |
| `/products/` | GET | ❌ | لیست محصولات |
| `/rewards/scan-products/` | POST | ⚠️ | اسکن QR |
| `/rewards/balance/` | GET | ✅ | موجودی امتیاز |
| `/rewards/history/` | GET | ✅ | تاریخچه امتیاز |
| `/rewards/redeem/` | POST | ✅ | استفاده از امتیاز |
| `/reviews/` | GET/POST | ⚠️ | نظرات |
| `/payments/initiate/` | POST | ✅ | شروع پرداخت |
| `/payments/orders/` | GET | ✅ | لیست سفارشات |
| `/notifications/register-device/` | POST | ✅ | ثبت دستگاه |

---

**نکته نهایی**: این راهنما شامل تمام endpointهای مورد نیاز برای اپلیکیشن React Native است. اگر endpoint جدیدی اضافه شد یا تغییری در ساختار API ایجاد شد، این فایل را به‌روز کنید.
