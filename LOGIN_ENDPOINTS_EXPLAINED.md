# 🔐 توضیح Endpoint های لاگین

## دو Endpoint لاگین وجود دارد:

---

## 1. `/api/accounts/login/` - ✅ **Endpoint اصلی لاگین** (توصیه می‌شود)

### 📝 فیلدهای Request:

```json
{
  "number": "09988776655",
  "password": "123qwe123"
}
```

- `number` - شماره تلفن
- `password` - رمز عبور

### 📥 Response:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 13,
    "username": "user_09988776655",
    "first_name": "علی",
    ...
  },
  "profile": {
    "id": 12,
    "role": "customer",
    "phone": "09988776655",
    ...
  }
}
```

### ✅ مزایا:
- فیلد `number` واضح‌تر است
- Response شامل `user` و `profile` است
- برای اپلیکیشن موبایل مناسب‌تر است

---

## 2. `/api/accounts/token/` - ⚙️ **Endpoint اضافی** (SimpleJWT استاندارد)

### 📝 فیلدهای Request:

```json
{
  "username": "user_09988776655",
  "password": "123qwe123"
}
```

یا:

```json
{
  "username": "09988776655",
  "password": "123qwe123"
}
```

- `username` - نام کاربری یا شماره تلفن
- `password` - رمز عبور

### 📥 Response:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### ⚙️ ویژگی‌ها:
- از Django REST Framework SimpleJWT استفاده می‌کند
- فقط tokens برمی‌گرداند (بدون user/profile)
- استاندارد SimpleJWT است

---

## 📊 مقایسه:

| ویژگی | `/api/accounts/login/` | `/api/accounts/token/` |
|-------|------------------------|------------------------|
| **فیلد شماره تلفن** | `number` ✅ | `username` |
| **فیلد رمز عبور** | `password` | `password` |
| **Response** | tokens + user + profile ✅ | فقط tokens |
| **استفاده** | برای اپلیکیشن موبایل ✅ | برای API عمومی |
| **توصیه** | ✅ **استفاده کنید** | ⚙️ اختیاری |

---

## ✅ توصیه:

**برای اپلیکیشن موبایل:** از `/api/accounts/login/` استفاده کنید

**دلایل:**
1. فیلد `number` واضح‌تر است
2. Response شامل `user` و `profile` است
3. نیازی به درخواست جداگانه برای دریافت اطلاعات کاربر نیست

---

## 📝 مثال استفاده:

### با `/api/accounts/login/` (توصیه می‌شود):

```javascript
// لاگین
const response = await axios.post('https://mywebsite.osc-fr1.scalingo.io/api/accounts/login/', {
  number: "09988776655",
  password: "123qwe123"
});

// همه چیز در یک response
const { access, refresh, user, profile } = response.data;

// ذخیره توکن
await AsyncStorage.setItem('access_token', access);
await AsyncStorage.setItem('refresh_token', refresh);

// اطلاعات کاربر و پروفایل هم آماده است
console.log(user);   // اطلاعات کاربر
console.log(profile); // اطلاعات پروفایل
```

### با `/api/accounts/token/` (اختیاری):

```javascript
// لاگین
const response = await axios.post('https://mywebsite.osc-fr1.scalingo.io/api/accounts/token/', {
  username: "user_09988776655",  // یا "09988776655"
  password: "123qwe123"
});

// فقط tokens
const { access, refresh } = response.data;

// ذخیره توکن
await AsyncStorage.setItem('access_token', access);
await AsyncStorage.setItem('refresh_token', refresh);

// باید جداگانه اطلاعات کاربر را بگیرید
const userResponse = await axios.get('/api/accounts/me/', {
  headers: {
    'Authorization': `Bearer ${access}`
  }
});
```

---

## 🎯 خلاصه:

### ✅ Endpoint اصلی: `/api/accounts/login/`
- فیلدها: `number`, `password`
- Response: tokens + user + profile
- **توصیه می‌شود برای اپلیکیشن موبایل**

### ⚙️ Endpoint اضافی: `/api/accounts/token/`
- فیلدها: `username`, `password`
- Response: فقط tokens
- برای سازگاری با استاندارد SimpleJWT

---

## ❓ چرا دو endpoint؟

1. **`/api/accounts/login/`** - برای اپلیکیشن موبایل (ساده‌تر و کامل‌تر)
2. **`/api/accounts/token/`** - برای سازگاری با استاندارد SimpleJWT (برای API عمومی)

---

## ✅ نتیجه:

**برای اپلیکیشن موبایل:** از `/api/accounts/login/` استفاده کنید ✅

این endpoint:
- فیلد `number` دارد (واضح‌تر)
- Response کامل است (tokens + user + profile)
- برای موبایل مناسب‌تر است

