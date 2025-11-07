# 🔑 نحوه استفاده از JWT Token

## ✅ توکن در Response

در response API، توکن به صورت **خام** (بدون "Bearer") برگردانده می‌شود:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**این درست است!** توکن در response نباید "Bearer" داشته باشد.

---

## 📤 استفاده از توکن در Request

وقتی می‌خواهید از توکن استفاده کنید، باید **"Bearer "** را قبل از توکن اضافه کنید:

### در Header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📝 مثال‌های استفاده

### 1. در Postman:

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. در React Native / JavaScript:

```javascript
const token = response.data.access; // توکن از response

// استفاده در header
axios.get('/api/accounts/me/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 3. در curl:

```bash
curl -X GET https://mywebsite.osc-fr1.scalingo.io/api/accounts/me/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. در Python:

```python
import requests

token = response.json()['access']  # توکن از response

headers = {
    'Authorization': f'Bearer {token}'
}

response = requests.get('https://mywebsite.osc-fr1.scalingo.io/api/accounts/me/', headers=headers)
```

---

## 🔍 تست با توکن شما

با توکنی که دریافت کردید:

```bash
# تست با curl
curl -X GET https://mywebsite.osc-fr1.scalingo.io/api/accounts/me/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYyNTgzOTI0LCJpYXQiOjE3NjI1NTUxMjQsImp0aSI6IjNkOTBiZDVjNDM5OTRhOWJiMjQzYmY4NTQ2NjAxYzgwIiwidXNlcl9pZCI6MTN9.VPJ32EHXgyW7e_k7kr6sjvmcSNVjqb0xirLpPGMAZTw"
```

---

## ✅ خلاصه

1. **در Response:** توکن خام است (بدون "Bearer") ✅
2. **در Request:** باید "Bearer " را اضافه کنید ✅
3. **فرمت:** `Authorization: Bearer <token>`

---

## 🎯 مثال کامل

### ثبت نام:
```json
POST /api/accounts/register/
Response: {
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### استفاده از توکن:
```json
GET /api/accounts/me/
Headers: {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## ⚠️ نکات مهم

1. **فاصله:** حتماً بین "Bearer" و توکن یک فاصله (space) باشد
2. **حساس به حروف:** "Bearer" باید با B بزرگ باشد
3. **توکن کامل:** توکن را کامل کپی کنید (خیلی طولانی است)

---

## 🔧 در اپلیکیشن موبایل

```javascript
// ذخیره توکن
await AsyncStorage.setItem('access_token', response.data.access);

// استفاده از توکن
const token = await AsyncStorage.getItem('access_token');
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

