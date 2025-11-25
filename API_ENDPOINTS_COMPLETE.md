# 📋 URLهای کامل API - منو، اسلایدر و جستجو

این فایل شامل URLهای کامل برای تست APIها روی دامین شماست.

---

## 🌐 Base URLs

**Versioned (توصیه می‌شود):**
```
https://your-domain.com/api/v1/
```

**Legacy (سازگاری با نسخه‌های قدیمی):**
```
https://your-domain.com/api/
```

---

## 1️⃣ API اسلایدر (Slider)

### URL کامل:

**Versioned:**
```
GET https://your-domain.com/api/v1/slider/
```

**Legacy:**
```
GET https://your-domain.com/api/slider/
```

### Query Parameters:

| پارامتر | نوع | الزامی | توضیحات |
|---------|-----|--------|---------|
| `business_id` | integer | ❌ خیر | فیلتر بر اساس ID کسب‌وکار |

### مثال‌های استفاده:

#### 1. دریافت همه اسلایدرها:
```
GET https://your-domain.com/api/v1/slider/
```

#### 2. دریافت اسلایدرهای یک کسب‌وکار خاص:
```
GET https://your-domain.com/api/v1/slider/?business_id=1
```

### Response Format:

```json
[
  {
    "image": "https://your-domain.com/media/sliders/image.jpg",
    "store": "Store Name",
    "address": "Store Address",
    "description": "Description",
    "business_id": 1,
    "stars": 4.5,
    "reviews_count": 20
  }
]
```

---

## 2️⃣ API منو (Menu)

### URL کامل:

**Versioned:**
```
GET https://your-domain.com/api/v1/menu/
```

**Legacy:**
```
GET https://your-domain.com/api/menu/
```

### Query Parameters:

| پارامتر | نوع | الزامی | توضیحات |
|---------|-----|--------|---------|
| `business_id` | integer | ❌ خیر | فیلتر بر اساس ID کسب‌وکار |

### مثال‌های استفاده:

#### 1. دریافت همه محصولات:
```
GET https://your-domain.com/api/v1/menu/
```

#### 2. دریافت محصولات یک کسب‌وکار خاص:
```
GET https://your-domain.com/api/v1/menu/?business_id=1
```

### Response Format:

```json
{
  "product": [
    {
      "id": 1,
      "image": "https://your-domain.com/media/products/image.jpg",
      "reward": "Free Coffee",
      "point": 10,
      "stars": 4.5
    }
  ]
}
```

---

## 3️⃣ API جستجو (Search)

### URL کامل:

**Versioned:**
```
GET https://your-domain.com/api/v1/search/
```

**Legacy:**
```
GET https://your-domain.com/api/search/
```

### Query Parameters:

| پارامتر | نوع | الزامی | توضیحات |
|---------|-----|--------|---------|
| `query` یا `q` | string | ✅ بله | متن جستجو (هر دو کار می‌کنند) |

### مثال‌های استفاده:

#### 1. جستجو با پارامتر `query`:
```
GET https://your-domain.com/api/v1/search/?query=restaurant
```

#### 2. جستجو با پارامتر `q` (سازگاری با نسخه‌های قدیمی):
```
GET https://your-domain.com/api/v1/search/?q=restaurant
```

#### 3. جستجو با کلمات چندتایی:
```
GET https://your-domain.com/api/v1/search/?query=coffee shop
```

#### 4. جستجو با URL Encoding:
```
GET https://your-domain.com/api/v1/search/?query=coffee%20shop
```

### Response Format:

```json
{
  "query": "restaurant",
  "results": {
    "businesses": [
      {
        "id": 1,
        "name": "Restaurant ABC",
        "description": "Description",
        "address": "123 Main St",
        "average_rating": 4.5,
        "review_count": 20
      }
    ],
    "products": [
      {
        "id": 1,
        "title": "Pizza",
        "price_cents": 25000,
        "points_reward": 10
      }
    ],
    "services": [
      {
        "id": 1,
        "name": "Delivery Service",
        "category": "food",
        "category_display": "Food",
        "description": "Fast delivery"
      }
    ]
  },
  "total": 3,
  "counts": {
    "businesses": 1,
    "products": 1,
    "services": 1
  }
}
```

---

## 🧪 تست با cURL

### تست API اسلایدر:
```bash
# همه اسلایدرها
curl -X GET "https://your-domain.com/api/v1/slider/"

# اسلایدرهای یک کسب‌وکار
curl -X GET "https://your-domain.com/api/v1/slider/?business_id=1"
```

### تست API منو:
```bash
# همه محصولات
curl -X GET "https://your-domain.com/api/v1/menu/"

# محصولات یک کسب‌وکار
curl -X GET "https://your-domain.com/api/v1/menu/?business_id=1"
```

### تست API جستجو:
```bash
# با query
curl -X GET "https://your-domain.com/api/v1/search/?query=restaurant"

# با q
curl -X GET "https://your-domain.com/api/v1/search/?q=restaurant"
```

---

## 🧪 تست با Postman

### 1. API اسلایدر:
- **Method:** GET
- **URL:** `https://your-domain.com/api/v1/slider/`
- **Query Params (اختیاری):**
  - Key: `business_id`
  - Value: `1`

### 2. API منو:
- **Method:** GET
- **URL:** `https://your-domain.com/api/v1/menu/`
- **Query Params (اختیاری):**
  - Key: `business_id`
  - Value: `1`

### 3. API جستجو:
- **Method:** GET
- **URL:** `https://your-domain.com/api/v1/search/`
- **Query Params (الزامی):**
  - Key: `query` یا `q`
  - Value: `restaurant`

---

## 🧪 تست با JavaScript (Fetch)

### API اسلایدر:
```javascript
// همه اسلایدرها
fetch('https://your-domain.com/api/v1/slider/')
  .then(response => response.json())
  .then(data => console.log(data));

// اسلایدرهای یک کسب‌وکار
fetch('https://your-domain.com/api/v1/slider/?business_id=1')
  .then(response => response.json())
  .then(data => console.log(data));
```

### API منو:
```javascript
// همه محصولات
fetch('https://your-domain.com/api/v1/menu/')
  .then(response => response.json())
  .then(data => console.log(data));

// محصولات یک کسب‌وکار
fetch('https://your-domain.com/api/v1/menu/?business_id=1')
  .then(response => response.json())
  .then(data => console.log(data));
```

### API جستجو:
```javascript
// با query
fetch('https://your-domain.com/api/v1/search/?query=restaurant')
  .then(response => response.json())
  .then(data => console.log(data));

// با q
fetch('https://your-domain.com/api/v1/search/?q=restaurant')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 🧪 تست با Axios

### API اسلایدر:
```javascript
import axios from 'axios';

// همه اسلایدرها
axios.get('https://your-domain.com/api/v1/slider/')
  .then(response => console.log(response.data));

// اسلایدرهای یک کسب‌وکار
axios.get('https://your-domain.com/api/v1/slider/', {
  params: { business_id: 1 }
})
  .then(response => console.log(response.data));
```

### API منو:
```javascript
// همه محصولات
axios.get('https://your-domain.com/api/v1/menu/')
  .then(response => console.log(response.data));

// محصولات یک کسب‌وکار
axios.get('https://your-domain.com/api/v1/menu/', {
  params: { business_id: 1 }
})
  .then(response => console.log(response.data));
```

### API جستجو:
```javascript
// با query
axios.get('https://your-domain.com/api/v1/search/', {
  params: { query: 'restaurant' }
})
  .then(response => console.log(response.data));

// با q
axios.get('https://your-domain.com/api/v1/search/', {
  params: { q: 'restaurant' }
})
  .then(response => console.log(response.data));
```

---

## ⚠️ نکات مهم:

1. **احراز هویت:** هیچکدام از این APIها نیاز به احراز هویت ندارند (`permissions.AllowAny`)

2. **HTTP Method:** همه از روش `GET` استفاده می‌کنند

3. **Content-Type:** Response به صورت `application/json` برمی‌گردد

4. **Error Handling:** در صورت خطا، کدهای HTTP مناسب برمی‌گردند:
   - `400 Bad Request`: پارامترهای نامعتبر
   - `404 Not Found`: منبع یافت نشد
   - `500 Internal Server Error`: خطای سرور

5. **URL Encoding:** برای جستجو با کلمات چندتایی، از URL encoding استفاده کنید:
   - `coffee shop` → `coffee%20shop`

---

## 📝 مثال کامل برای تست:

```bash
# 1. تست اسلایدر
curl "https://your-domain.com/api/v1/slider/"

# 2. تست منو
curl "https://your-domain.com/api/v1/menu/"

# 3. تست جستجو
curl "https://your-domain.com/api/v1/search/?query=test"
```

---

**نکته:** `your-domain.com` را با دامین واقعی خود جایگزین کنید (مثلاً `mybonusberlin.de`)

