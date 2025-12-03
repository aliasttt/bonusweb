# راهنمای تست کش تصاویر در Scalingo

## هدف
بررسی اینکه آیا تصاویر در دیتابیس ذخیره شده‌اند و بعد از deploy پاک نمی‌شوند.

## دستورات Scalingo CLI

### 1. تست کش تصاویر

```powershell
# تست کامل کش تصاویر
scalingo --app mywebsite run python test_image_cache_scalingo.py
```

یا:

```powershell
# استفاده از shell
scalingo --app mywebsite run python manage.py shell < test_image_cache_scalingo.py
```

### 2. کش کردن همه تصاویر (اگر کش نشده باشند)

```powershell
# کش کردن همه تصاویر موجود
scalingo --app mywebsite run python manage.py shell < test_image_cache.py
```

یا:

```powershell
# استفاده از API endpoint
scalingo --app mywebsite run python manage.py shell
# سپس در shell:
from loyalty.image_cache import ImageCacheManager
result = ImageCacheManager.cache_all_images()
print(f"Cached: {result['cached']}, Errors: {result['errors']}")
```

### 3. بررسی وضعیت کش

```powershell
# بررسی تعداد کش‌ها
scalingo --app mywebsite run python manage.py shell
# سپس در shell:
from loyalty.models import ImageCache
print(f"Total cached images: {ImageCache.objects.count()}")
```

### 4. بررسی تصاویر خاص

```powershell
scalingo --app mywebsite run python manage.py shell
# سپس در shell:
from loyalty.models import ImageCache, Product
product = Product.objects.first()
if product and product.image:
    cache = ImageCache.objects.filter(
        content_type='loyalty.product',
        object_id=product.id
    ).first()
    if cache:
        print(f"Image cached: {cache.original_path}")
        print(f"Has base64: {bool(cache.image_data)}")
        print(f"Has URL: {bool(cache.image_url)}")
    else:
        print("Image not cached!")
```

## تست بعد از Deploy

### مراحل:

1. **قبل از Deploy:**
   ```powershell
   # تست و کش کردن تصاویر
   scalingo --app mywebsite run python test_image_cache_scalingo.py
   ```

2. **Deploy کنید:**
   ```powershell
   git push scalingo main
   ```

3. **بعد از Deploy:**
   ```powershell
   # دوباره تست کنید
   scalingo --app mywebsite run python test_image_cache_scalingo.py
   ```

4. **بررسی کنید:**
   - آیا تعداد کش‌ها همان است؟
   - آیا تصاویر هنوز در دیتابیس هستند؟
   - آیا می‌توانید از کش بازیابی کنید؟

## نتیجه مورد انتظار

اگر همه چیز درست باشد، باید ببینید:

```
✅ مدل ImageCache موجود است
📊 تعداد تصاویر کش شده در دیتابیس: X
✅ تصاویر دارای داده کامل: X/X
✅ تصاویر در دیتابیس ذخیره شده‌اند!
✅ این تصاویر بعد از deploy پاک نمی‌شوند!
```

## عیب‌یابی

### مشکل: هیچ تصویری کش نشده

**راه حل:**
```powershell
# کش کردن همه تصاویر
scalingo --app mywebsite run python manage.py shell < test_image_cache.py
```

### مشکل: Migration اجرا نشده

**راه حل:**
```powershell
# اجرای migration
scalingo --app mywebsite run python manage.py migrate loyalty
```

### مشکل: تصاویر فقط URL دارند (نه base64)

**راه حل:**
- این طبیعی است برای تصاویر بزرگ
- برای اطمینان بیشتر، Cloudinary را فعال کنید:
  ```powershell
  scalingo env-set USE_CLOUDINARY=1
  scalingo env-set CLOUDINARY_CLOUD_NAME=your-cloud-name
  scalingo env-set CLOUDINARY_API_KEY=your-api-key
  scalingo env-set CLOUDINARY_API_SECRET=your-api-secret
  ```

## دستورات سریع

```powershell
# تست کامل
scalingo --app mywebsite run python test_image_cache_scalingo.py

# کش کردن همه تصاویر
scalingo --app mywebsite run python manage.py shell < test_image_cache.py

# بررسی تعداد
scalingo --app mywebsite run python manage.py shell -c "from loyalty.models import ImageCache; print(ImageCache.objects.count())"

# مشاهده لاگ‌ها
scalingo --app mywebsite logs --follow
```

## نکات مهم

1. **Migration**: حتماً migration را اجرا کنید قبل از تست
2. **Cloudinary**: برای بهترین نتیجه، Cloudinary را فعال کنید
3. **بکاپ**: قبل از deploy، از دیتابیس بکاپ بگیرید
4. **تست**: بعد از deploy، حتماً تست کنید

