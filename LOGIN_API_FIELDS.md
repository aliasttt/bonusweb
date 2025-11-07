# 🔐 فیلدهای API لاگین

## دو Endpoint لاگین وجود دارد:

---

## 1. `POST /api/accounts/login/` - لاگین با شماره تلفن

### 📝 فیلدهای Request:

| فیلد | نوع | Required | توضیحات |
|------|-----|----------|---------|
| `number` | string | ✅ بله | شماره تلفن |
| `password` | string | ✅ بله | رمز عبور |

### 📤 مثال Request:

```json
{
  "number": "09988776655",
  "password": "123qwe123"
}
```

### 📥 مثال Response (200 OK):

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 13,
    "username": "user_09988776655",
    "first_name": "tetetet",
    "last_name": "",
    "email": "",
    "date_joined": "2025-11-08T02:08:43.855353+03:30",
    "is_active": true
  },
  "profile": {
    "id": 12,
    "role": "customer",
    "phone": "09988776655",
    ...
  }
}
```

### 🔍 منطق:
- کاربر را با شماره تلفن (`number`) پیدا می‌کند
- رمز عبور را بررسی می‌کند
- JWT tokens برمی‌گرداند

---

## 2. `POST /api/accounts/token/` - لاگین با Username (SimpleJWT)

### 📝 فیلدهای Request:

| فیلد | نوع | Required | توضیحات |
|------|-----|----------|---------|
| `username` | string | ✅ بله | نام کاربری یا شماره تلفن |
| `password` | string | ✅ بله | رمز عبور |

### 📤 مثال Request:

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

### 📥 مثال Response (200 OK):

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 🔍 منطق:
- از Django REST Framework SimpleJWT استفاده می‌کند
- با `username` یا `password` لاگین می‌کند
- فقط JWT tokens برمی‌گرداند (بدون user/profile)

---

## 📊 مقایسه دو Endpoint:

| ویژگی | `/api/accounts/login/` | `/api/accounts/token/` |
|-------|------------------------|------------------------|
| **فیلد شماره تلفن** | `number` | `username` |
| **فیلد رمز عبور** | `password` | `password` |
| **Response** | tokens + user + profile | فقط tokens |
| **استفاده** | برای اپلیکیشن موبایل | برای API عمومی |

---

## ✅ توصیه:

**برای اپلیکیشن موبایل:** از `/api/accounts/login/` استفاده کنید
- فیلد `number` واضح‌تر است
- Response شامل user و profile است

**برای API عمومی:** از `/api/accounts/token/` استفاده کنید
- استاندارد SimpleJWT
- فقط tokens برمی‌گرداند

---

## 📝 مثال‌های استفاده:

### 1. با `/api/accounts/login/`:

```javascript
// React Native / JavaScript
const response = await axios.post('https://mywebsite.osc-fr1.scalingo.io/api/accounts/login/', {
  number: "09988776655",
  password: "123qwe123"
});

const { access, refresh, user, profile } = response.data;
```

### 2. با `/api/accounts/token/`:

```javascript
// React Native / JavaScript
const response = await axios.post('https://mywebsite.osc-fr1.scalingo.io/api/accounts/token/', {
  username: "user_09988776655",  // یا "09988776655"
  password: "123qwe123"
});

const { access, refresh } = response.data;
```

---

## 🎯 خلاصه:

### Endpoint 1: `/api/accounts/login/`
- فیلدها: `number`, `password`
- Response: tokens + user + profile

### Endpoint 2: `/api/accounts/token/`
- فیلدها: `username`, `password`
- Response: فقط tokens

