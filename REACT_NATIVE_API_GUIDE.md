# راهنمای API برای React Native

## 🔑 Endpoint جدید: اسکن QR با محصولات

### POST `/api/rewards/scan-products/`

این endpoint برای React Native app شما طراحی شده است که QR کدهای تولید شده در صفحه Partner را پردازش می‌کند.

#### درخواست (Request)

```json
{
  "business_id": 1,
  "product_ids": [1, 2, 3],
  "phone": "09123456789"
}
```

#### پارامترها:
- **business_id** (required): شناسه کسب‌وکار
- **product_ids** (required): آرایه شناسه محصولات انتخاب شده در QR
- **phone** (required برای کاربران جدید): شماره تلفن کاربر

#### پاسخ موفقیت‌آمیز (Success Response - 201)

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

#### پاسخ خطا (Error Responses)

**400 Bad Request** - فیلدهای لازم ناقص هستند:
```json
{
  "error": "business_id is required"
}
```

**400 Bad Request** - محصولات پیدا نشدند:
```json
{
  "error": "Some products not found or not active",
  "found_products": [1, 2]
}
```

**400 Bad Request** - کاربر جدید نیاز به شماره تلفن دارد:
```json
{
  "error": "phone is required for new users",
  "requires_registration": true
}
```

**404 Not Found** - کسب‌وکار پیدا نشد:
```json
{
  "error": "Business not found"
}
```

---

## 📱 نحوه استفاده در React Native

### مثال کد JavaScript/TypeScript:

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://your-server.com/api';

async function scanQRCode(qrData) {
  try {
    // qrData از QR code خوانده می‌شود
    // qrData = { business_id: 1, product_ids: [1, 2], total_points: 25 }
    
    const phone = await getUserPhone(); // دریافت شماره تلفن از کاربر
    
    const response = await axios.post(
      `${API_BASE_URL}/rewards/scan-products/`,
      {
        business_id: qrData.business_id,
        product_ids: qrData.product_ids,
        phone: phone
      }
    );
    
    if (response.data.success) {
      // ذخیره اطلاعات در دیتابیس محلی
      await saveToLocalDatabase({
        transaction_id: response.data.transaction_id,
        business_id: response.data.business_id,
        business_name: response.data.business_name,
        total_points: response.data.total_points_awarded,
        current_balance: response.data.current_balance,
        products: response.data.products,
        timestamp: new Date().toISOString()
      });
      
      // نمایش پیام موفقیت
      Alert.alert(
        'موفقیت!',
        `امتیاز دریافت شد: ${response.data.total_points_awarded} امتیاز\n` +
        `موجودی فعلی: ${response.data.current_balance} امتیاز`
      );
      
      return response.data;
    }
  } catch (error) {
    if (error.response) {
      // خطای سرور
      console.error('API Error:', error.response.data);
      
      if (error.response.status === 400 && error.response.data.requires_registration) {
        // کاربر جدید نیاز به شماره تلفن دارد
        Alert.alert(
          'ثبت نام',
          'لطفاً شماره تلفن خود را وارد کنید'
        );
      } else {
        Alert.alert('خطا', error.response.data.error || 'خطا در پردازش درخواست');
      }
    } else {
      // خطای شبکه
      Alert.alert('خطای شبکه', 'لطفاً اتصال اینترنت خود را بررسی کنید');
    }
    throw error;
  }
}

// تابع کمکی برای ذخیره در دیتابیس محلی
async function saveToLocalDatabase(data) {
  // استفاده از AsyncStorage یا SQLite
  // مثال:
  // await AsyncStorage.setItem(`transaction_${data.transaction_id}`, JSON.stringify(data));
}
```

---

## 🔄 Flow کامل برای کاربر جدید:

1. **اسکن QR**: کاربر QR کد را اسکن می‌کند
2. **دریافت شماره**: اگر کاربر جدید بود، شماره تلفن را از او می‌گیرید
3. **ارسال درخواست**: درخواست POST به `/api/rewards/scan-products/` ارسال می‌شود
4. **پردازش در سرور**:
   - اگر کاربر جدید بود، حساب کاربری با شماره تلفن ساخته می‌شود
   - محصولات بررسی می‌شوند و امتیاز محاسبه می‌شود
   - تراکنش در دیتابیس ذخیره می‌شود
5. **دریافت پاسخ**: پاسخ کامل با تمام اطلاعات برمی‌گردد
6. **ذخیره محلی**: اطلاعات در دیتابیس محلی React Native ذخیره می‌شود

---

## ✅ تست کردن API

برای تست کردن API، از اسکریپت Python استفاده کنید:

```bash
python test_api_endpoints.py
```

یا با curl:

```bash
curl -X POST http://127.0.0.1:8000/api/rewards/scan-products/ \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1,
    "product_ids": [1, 2],
    "phone": "09123456789"
  }'
```

---

## 📊 فیلدهای Response برای ذخیره در دیتابیس:

- `transaction_id`: شناسه یکتا تراکنش
- `user_id`: شناسه کاربر
- `customer_id`: شناسه مشتری
- `business_id`: شناسه کسب‌وکار
- `business_name`: نام کسب‌وکار
- `products`: لیست محصولات با جزئیات
- `total_points_awarded`: مجموع امتیاز دریافت شده
- `current_balance`: موجودی فعلی امتیاز
- `wallet_id`: شناسه والت
- `is_new_user`: آیا کاربر جدید بود یا نه

تمام این اطلاعات قابل ذخیره در دیتابیس محلی React Native هستند.

