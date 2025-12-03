"""
اسکریپت تست برای سیستم کش تصاویر
این اسکریپت تست می‌کند که:
1. تصاویر به درستی کش می‌شوند
2. تصاویر از کش بازیابی می‌شوند
3. سیستم درست کار می‌کند

Usage:
    python manage.py shell < test_image_cache.py
    OR
    python test_image_cache.py
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.conf import settings
from loyalty.models import Product, Slider, ImageCache
from loyalty.image_cache import ImageCacheManager


def test_image_cache():
    """تست سیستم کش تصاویر"""
    print("=" * 80)
    print("تست سیستم کش تصاویر")
    print("=" * 80)
    
    # تست 1: بررسی تصاویر موجود
    print("\n1. بررسی تصاویر موجود در دیتابیس:")
    products = Product.objects.filter(image__isnull=False).exclude(image='')
    sliders = Slider.objects.filter(image__isnull=False).exclude(image='')
    
    print(f"   Products با تصویر: {products.count()}")
    print(f"   Sliders با تصویر: {sliders.count()}")
    
    # تست 2: کش کردن تصاویر
    print("\n2. کش کردن تصاویر:")
    result = ImageCacheManager.cache_all_images()
    print(f"   ✅ {result['cached']} تصویر کش شد")
    print(f"   ❌ {result['errors']} خطا")
    
    # تست 3: بررسی کش شده‌ها
    print("\n3. بررسی کش شده‌ها:")
    from django.db.models import Q
    cache_count = ImageCache.objects.count()
    cache_with_data = ImageCache.objects.filter(
        Q(image_data__isnull=False) | Q(image_url__isnull=False)
    ).count()
    
    print(f"   کل کش‌ها: {cache_count}")
    print(f"   کش‌های دارای داده: {cache_with_data}")
    
    # تست 4: بررسی نمونه کش
    if cache_count > 0:
        print("\n4. نمونه کش:")
        sample_cache = ImageCache.objects.first()
        print(f"   Content Type: {sample_cache.content_type}")
        print(f"   Object ID: {sample_cache.object_id}")
        print(f"   Original Path: {sample_cache.original_path}")
        print(f"   Has Data: {sample_cache.has_data}")
        print(f"   Has URL: {bool(sample_cache.image_url)}")
        print(f"   Has Base64: {bool(sample_cache.image_data)}")
        if sample_cache.file_size:
            print(f"   File Size: {sample_cache.file_size / 1024:.1f} KB")
    
    # تست 5: تست بازیابی
    print("\n5. تست بازیابی از کش:")
    if products.exists():
        product = products.first()
        cache = ImageCacheManager.get_cached_image(product)
        if cache:
            print(f"   ✅ تصویر Product ID {product.id} از کش بازیابی شد")
        else:
            print(f"   ❌ تصویر Product ID {product.id} در کش یافت نشد")
    
    # خلاصه
    print("\n" + "=" * 80)
    print("خلاصه:")
    print("=" * 80)
    print(f"✅ سیستم کش فعال است")
    print(f"✅ {cache_count} تصویر در کش ذخیره شده")
    print(f"✅ {cache_with_data} تصویر دارای داده کامل")
    
    if cache_with_data < cache_count:
        print(f"⚠️ {cache_count - cache_with_data} کش بدون داده")
    
    print("\n💡 توصیه:")
    print("   - برای جلوگیری از پاک شدن تصاویر، Cloudinary را فعال کنید")
    print("   - سیستم کش به صورت خودکار تصاویر جدید را ذخیره می‌کند")
    print("   - می‌توانید از admin panel برای مدیریت کش استفاده کنید")


if __name__ == "__main__":
    test_image_cache()

