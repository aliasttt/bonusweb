# 🔑 JWT Token چیست و برای چه استفاده می‌شود؟

## 🎯 توکن برای چیست؟

**JWT Token** برای **احراز هویت (Authentication)** استفاده می‌شود.

---

## 📖 توضیح ساده:

بعد از **ثبت‌نام** یا **لاگین**، شما یک **توکن** دریافت می‌کنید. این توکن مثل یک **کارت شناسایی** است که نشان می‌دهد شما چه کسی هستید.

---

## 🔄 چرخه کار:

### 1. ثبت‌نام / لاگین:
```
کاربر → API → توکن دریافت می‌کند
```

**مثال:**
```json
POST /api/accounts/register/
{
  "number": "09988776655",
  "name": "علی",
  "password": "123qwe123",
  ...
}

Response:
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  ← این توکن است
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. استفاده از توکن در درخواست‌های بعدی:
```
کاربر → API (با توکن) → سرور می‌فهمد شما چه کسی هستید
```

**مثال:**
```json
GET /api/accounts/me/
Headers:
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response:
{
  "id": 13,
  "username": "user_09988776655",
  "first_name": "علی",
  ...
}
```

---

## 🎯 کاربردهای توکن:

### 1. **احراز هویت (Authentication)**
- سرور می‌فهمد شما چه کسی هستید
- بدون نیاز به ارسال username/password در هر درخواست

### 2. **دسترسی به API های محافظت شده**
- بعضی API ها نیاز به لاگین دارند
- با توکن می‌توانید به آن‌ها دسترسی پیدا کنید

### 3. **امنیت**
- توکن منقضی می‌شود (expires)
- اگر توکن به سرقت برود، می‌توانید آن را باطل کنید

---

## 📋 انواع توکن:

### 1. **Access Token** (`access`)
- برای دسترسی به API ها
- مدت زمان: 8 ساعت (در تنظیمات شما)
- استفاده: در header `Authorization: Bearer <access_token>`

### 2. **Refresh Token** (`refresh`)
- برای دریافت access token جدید
- مدت زمان: 30 روز (در تنظیمات شما)
- استفاده: وقتی access token منقضی شد

---

## 🔄 مثال کامل:

### مرحله 1: ثبت‌نام
```javascript
// ثبت‌نام
const registerResponse = await axios.post('/api/accounts/register/', {
  number: "09988776655",
  name: "علی",
  password: "123qwe123",
  ...
});

// توکن‌ها را ذخیره کنید
const accessToken = registerResponse.data.access;
const refreshToken = registerResponse.data.refresh;

// ذخیره در AsyncStorage (React Native)
await AsyncStorage.setItem('access_token', accessToken);
await AsyncStorage.setItem('refresh_token', refreshToken);
```

### مرحله 2: استفاده از توکن
```javascript
// دریافت اطلاعات کاربر
const accessToken = await AsyncStorage.getItem('access_token');

const userResponse = await axios.get('/api/accounts/me/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

console.log(userResponse.data); // اطلاعات کاربر
```

### مرحله 3: اگر توکن منقضی شد
```javascript
// اگر access token منقضی شد، از refresh token استفاده کنید
const refreshToken = await AsyncStorage.getItem('refresh_token');

const refreshResponse = await axios.post('/api/accounts/token/refresh/', {
  refresh: refreshToken
});

// access token جدید را ذخیره کنید
const newAccessToken = refreshResponse.data.access;
await AsyncStorage.setItem('access_token', newAccessToken);
```

---

## 🛡️ امنیت:

### ✅ مزایا:
1. **امن**: توکن hash شده است
2. **منقضی می‌شود**: بعد از 8 ساعت باید refresh کنید
3. **بدون نیاز به password**: بعد از لاگین، password لازم نیست

### ⚠️ نکات امنیتی:
1. **توکن را محرمانه نگه دارید**: مثل password
2. **HTTPS استفاده کنید**: توکن را فقط روی HTTPS ارسال کنید
3. **توکن منقضی شده را refresh کنید**: از refresh token استفاده کنید

---

## 📝 خلاصه:

| سوال | جواب |
|------|------|
| **توکن برای چیست؟** | احراز هویت (Authentication) |
| **چطور استفاده می‌شود؟** | در header: `Authorization: Bearer <token>` |
| **چقدر اعتبار دارد؟** | Access: 8 ساعت، Refresh: 30 روز |
| **چرا استفاده می‌شود؟** | بدون نیاز به ارسال password در هر درخواست |

---

## 🎯 مثال واقعی:

### بدون توکن (❌ ناامن):
```javascript
// باید در هر درخواست password بفرستید
axios.get('/api/accounts/me/', {
  username: "user_09988776655",
  password: "123qwe123"  // ❌ ناامن!
});
```

### با توکن (✅ امن):
```javascript
// فقط یک بار لاگین می‌کنید
const token = await AsyncStorage.getItem('access_token');

axios.get('/api/accounts/me/', {
  headers: {
    'Authorization': `Bearer ${token}`  // ✅ امن!
  }
});
```

---

## ✅ نتیجه:

**توکن = کارت شناسایی دیجیتال**

- یک بار لاگین می‌کنید
- توکن دریافت می‌کنید
- در درخواست‌های بعدی از توکن استفاده می‌کنید
- سرور می‌فهمد شما چه کسی هستید

