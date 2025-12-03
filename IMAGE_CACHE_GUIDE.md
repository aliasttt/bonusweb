# راهنمای سیستم کش تصاویر

## مشکل
در Scalingo، فایل‌سیستم ephemeral است و فایل‌های آپلود شده بعد از هر deploy پاک می‌شوند. این باعث می‌شود تصاویر از دست بروند.

## راه حل
سیستم کش تصاویر که تصاویر را در دیتابیس ذخیره می‌کند تا از پاک شدن جلوگیری شود.

## ویژگی‌ها

### 1. ذخیره خودکار
- تصاویر به صورت خودکار هنگام آپلود در کش ذخیره می‌شوند
- از signal های Django استفاده می‌کند

### 2. ذخیره به دو روش
- **Base64**: برای تصاویر کوچک (تا 5MB)
- **URL**: برای تصاویر بزرگ یا در Cloudinary

### 3. بازیابی خودکار
- در صورت پاک شدن فایل اصلی، می‌توان از کش بازیابی کرد

## استفاده

### 1. فعال کردن سیستم
سیستم به صورت خودکار فعال است. فقط migration را اجرا کنید:

```bash
python manage.py migrate
```

### 2. کش کردن همه تصاویر موجود
```python
from loyalty.image_cache import ImageCacheManager

# کش کردن همه تصاویر
result = ImageCacheManager.cache_all_images()
print(f"{result['cached']} تصویر کش شد")
```

### 3. بررسی وضعیت کش
```python
from loyalty.models import ImageCache

# تعداد کش‌ها
cache_count = ImageCache.objects.count()

# کش‌های دارای داده
cache_with_data = ImageCache.objects.filter(
    Q(image_data__isnull=False) | Q(image_url__isnull=False)
).count()
```

### 4. استفاده از API

#### بررسی وضعیت کش
```bash
GET /partners/image-cache/status/
```

#### کش کردن همه تصاویر
```bash
POST /partners/image-cache/cache-all/
```

### 5. استفاده از Admin Panel
1. به `/admin/` بروید
2. بخش "Image Caches" را باز کنید
3. می‌توانید کش‌ها را مشاهده و مدیریت کنید

## اسکریپت‌های دیباگ

### بررسی وضعیت تصاویر
```bash
python manage.py shell < debug_image_storage.py
```

### تست سیستم کش
```bash
python manage.py shell < test_image_cache.py
```

## مدل ImageCache

### فیلدها
- `content_type`: نوع مدل (مثلاً loyalty.product)
- `object_id`: ID شیء در مدل اصلی
- `original_path`: مسیر اصلی فایل
- `image_data`: تصویر به صورت base64
- `image_url`: URL تصویر در storage
- `file_size`: حجم فایل
- `content_type_header`: Content-Type (مثلاً image/jpeg)
- `created_at`: زمان ایجاد
- `updated_at`: زمان به‌روزرسانی
- `last_accessed`: آخرین زمان دسترسی

## نکات مهم

1. **Cloudinary**: برای بهترین نتیجه، Cloudinary را فعال کنید
2. **حجم**: تصاویر بزرگ (بیش از 5MB) فقط URL ذخیره می‌شوند
3. **Performance**: کش در دیتابیس است، پس حجم دیتابیس افزایش می‌یابد
4. **Cleanup**: می‌توانید کش‌های قدیمی را پاک کنید:
   ```python
   ImageCacheManager.cleanup_old_cache(days=90)
   ```

## عیب‌یابی

### تصاویر کش نمی‌شوند
1. بررسی کنید که signal ها فعال هستند
2. بررسی کنید که migration اجرا شده است
3. لاگ‌ها را بررسی کنید

### تصاویر از کش بازیابی نمی‌شوند
1. بررسی کنید که کش دارای داده است
2. بررسی کنید که مسیر فایل درست است
3. از `ImageCacheManager.get_cached_image()` استفاده کنید

## مثال‌ها

### کش کردن یک تصویر خاص
```python
from loyalty.models import Product
from loyalty.image_cache import ImageCacheManager

product = Product.objects.get(id=1)
cache = ImageCacheManager.cache_image(product)
```

### بازیابی از کش
```python
cache = ImageCacheManager.get_cached_image(product)
if cache and cache.has_data:
    if cache.image_data:
        # استفاده از base64
        image_bytes = base64.b64decode(cache.image_data)
    elif cache.image_url:
        # استفاده از URL
        image_url = cache.image_url
```

## پشتیبانی

برای مشکلات یا سوالات:
1. اسکریپت `debug_image_storage.py` را اجرا کنید
2. لاگ‌ها را بررسی کنید
3. Admin panel را بررسی کنید

