# راهنمای استفاده از Unsplash API

## تنظیمات اولیه

### 1. تنظیم Credentials در Scalingo

```powershell
scalingo --app mywebsite env-set UNSPLASH_ACCESS_KEY=25NXFDLC2DJM5VSPEPRWUWIJPUYARVYUOHJYK15K2CKC33XV
scalingo --app mywebsite env-set UNSPLASH_SECRET_KEY=K32DJAKBJPR5HWNMDI3EEOTMLQMTGTOD40NPSRMOTKHVVIPN
```

بعد از تنظیم، restart کن:
```powershell
scalingo --app mywebsite restart
```

## API Endpoint

### URL
```
GET /api/v1/unsplash/search/
GET /api/unsplash/search/  (legacy)
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | No | "restaurant" | کلمه کلیدی جستجو |
| `location` | string | No | - | نام مکان (مثلاً "paris", "tehran") |
| `per_page` | integer | No | 10 | تعداد نتایج (حداکثر 30) |
| `page` | integer | No | 1 | شماره صفحه |
| `orientation` | string | No | - | جهت عکس: "landscape", "portrait", "squarish" |
| `order_by` | string | No | "popular" | ترتیب: "latest", "oldest", "popular", "views", "downloads" |

## مثال‌های استفاده

### 1. جستجوی ساده
```
GET /api/v1/unsplash/search/?query=restaurant
```

### 2. جستجو با location
```
GET /api/v1/unsplash/search/?query=food&location=paris
```

### 3. جستجو با تعداد بیشتر
```
GET /api/v1/unsplash/search/?query=coffee&per_page=20
```

### 4. جستجو با orientation
```
GET /api/v1/unsplash/search/?query=restaurant&orientation=landscape
```

### 5. جستجوی کامل
```
GET /api/v1/unsplash/search/?query=food&location=tehran&per_page=15&page=1&orientation=portrait&order_by=latest
```

## Response Format

```json
{
  "query": "restaurant paris",
  "total": 1500,
  "total_pages": 50,
  "page": 1,
  "per_page": 10,
  "results": [
    {
      "id": "abc123",
      "description": "Beautiful restaurant interior",
      "urls": {
        "raw": "https://images.unsplash.com/...",
        "full": "https://images.unsplash.com/...",
        "regular": "https://images.unsplash.com/...",
        "small": "https://images.unsplash.com/...",
        "thumb": "https://images.unsplash.com/..."
      },
      "width": 4000,
      "height": 3000,
      "color": "#a8a8a8",
      "likes": 150,
      "location": {
        "name": "Paris, France",
        "city": "Paris",
        "country": "France",
        "position": {
          "latitude": 48.8566,
          "longitude": 2.3522
        }
      },
      "user": {
        "id": "user123",
        "username": "photographer",
        "name": "John Doe",
        "profile_image": "https://..."
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## استفاده در Frontend (JavaScript)

```javascript
// جستجوی ساده
fetch('https://mywebsite.osc-fr1.scalingo.io/api/v1/unsplash/search/?query=restaurant')
  .then(response => response.json())
  .then(data => {
    console.log(data.results);
    // نمایش عکس‌ها
    data.results.forEach(photo => {
      console.log(photo.urls.regular);
    });
  });
```

## استفاده در React Native

```javascript
const fetchImages = async (query, location) => {
  try {
    const url = `https://mywebsite.osc-fr1.scalingo.io/api/v1/unsplash/search/?query=${query}&location=${location}&per_page=20`;
    const response = await fetch(url);
    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('Error fetching images:', error);
    return [];
  }
};
```

## Cache

نتایج برای 1 ساعت cache می‌شوند تا سرعت پاسخ بیشتر شود.

## Error Handling

### اگر Unsplash API تنظیم نشده باشد:
```json
{
  "error": "Unsplash API not configured",
  "detail": "UNSPLASH_ACCESS_KEY is not set"
}
```

### اگر خطای شبکه باشد:
```json
{
  "error": "Network error",
  "detail": "Failed to connect to Unsplash API: ..."
}
```

## نکات مهم

1. **Rate Limiting**: Unsplash API محدودیت دارد (50 درخواست در ساعت برای free tier)
2. **Cache**: نتایج cache می‌شوند تا از rate limit جلوگیری شود
3. **Security**: API Key در environment variables ذخیره می‌شود و هرگز در response نمایش داده نمی‌شود
4. **Location**: اگر location در query parameter باشد، با query ترکیب می‌شود

