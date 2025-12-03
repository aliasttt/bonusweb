"""
اسکریپت تست برای بررسی کش تصاویر در Scalingo
این اسکریپت بررسی می‌کند که:
1. آیا ImageCache در دیتابیس وجود دارد؟
2. آیا تصاویر کش شده‌اند؟
3. آیا بعد از deploy تصاویر پاک می‌شوند یا نه؟

Usage در Scalingo:
    scalingo --app mywebsite run python manage.py shell < test_image_cache_scalingo.py
    OR
    scalingo --app mywebsite run python test_image_cache_scalingo.py
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from loyalty.models import Product, Slider, ImageCache, Business
from loyalty.image_cache import ImageCacheManager


def print_section(title):
    """چاپ عنوان بخش"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_image_cache_in_database():
    """تست کش تصاویر در دیتابیس"""
    print_section("تست کش تصاویر در دیتابیس")
    
    # بررسی ImageCache
    try:
        cache_count = ImageCache.objects.count()
        print(f"\n✅ مدل ImageCache موجود است")
        print(f"📊 تعداد تصاویر کش شده در دیتابیس: {cache_count}")
        
        if cache_count == 0:
            print("\n⚠️ هیچ تصویری در کش وجود ندارد!")
            print("   باید تصاویر را کش کنید:")
            print("   python manage.py shell < test_image_cache.py")
            return False
        
        # بررسی کش‌های دارای داده
        from django.db.models import Q
        cache_with_data = ImageCache.objects.filter(
            Q(image_data__isnull=False) | Q(image_url__isnull=False)
        ).count()
        
        print(f"✅ تصاویر دارای داده کامل: {cache_with_data}/{cache_count}")
        
        # نمایش نمونه‌ها
        print("\n📸 نمونه تصاویر کش شده:")
        sample_caches = ImageCache.objects.all()[:5]
        for cache in sample_caches:
            print(f"\n  - ID {cache.id}:")
            print(f"    Content Type: {cache.content_type}")
            print(f"    Object ID: {cache.object_id}")
            print(f"    Original Path: {cache.original_path}")
            print(f"    Has Base64: {'Yes' if cache.image_data else 'No'}")
            print(f"    Has URL: {'Yes' if cache.image_url else 'No'}")
            if cache.file_size:
                print(f"    File Size: {cache.file_size / 1024:.1f} KB")
            print(f"    Created: {cache.created_at}")
        
        if cache_count > 5:
            print(f"\n  ... و {cache_count - 5} تصویر دیگر")
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطا در بررسی ImageCache: {e}")
        print("   احتمالاً migration اجرا نشده است!")
        return False


def test_products_and_sliders():
    """بررسی Products و Sliders"""
    print_section("بررسی Products و Sliders")
    
    products = Product.objects.filter(image__isnull=False).exclude(image='')
    sliders = Slider.objects.filter(image__isnull=False).exclude(image='')
    
    print(f"\n📦 Products با تصویر: {products.count()}")
    print(f"🖼️ Sliders با تصویر: {sliders.count()}")
    
    # بررسی اینکه آیا در کش هستند
    if products.count() > 0 or sliders.count() > 0:
        print("\nبررسی کش شدن:")
        
        products_cached = 0
        sliders_cached = 0
        
        for product in products[:10]:
            cache = ImageCacheManager.get_cached_image(product)
            if cache:
                products_cached += 1
        
        for slider in sliders[:10]:
            cache = ImageCacheManager.get_cached_image(slider)
            if cache:
                sliders_cached += 1
        
        print(f"  Products کش شده: {products_cached}/{min(products.count(), 10)}")
        print(f"  Sliders کش شده: {sliders_cached}/{min(sliders.count(), 10)}")


def test_storage_backend():
    """بررسی storage backend"""
    print_section("بررسی Storage Backend")
    
    print(f"Storage Class: {type(default_storage).__name__}")
    print(f"Storage Module: {type(default_storage).__module__}")
    print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
    
    import os
    use_cloudinary = os.environ.get('USE_CLOUDINARY', '0') == '1'
    print(f"\nUSE_CLOUDINARY: {use_cloudinary}")
    
    if 'cloudinary' in str(getattr(settings, 'DEFAULT_FILE_STORAGE', '')).lower():
        print("✅ Cloudinary فعال است - فایل‌ها در cloud ذخیره می‌شوند")
    else:
        print("⚠️ Cloudinary فعال نیست - فایل‌ها در فایل‌سیستم محلی هستند")
        print("   در Scalingo این فایل‌ها بعد از هر deploy پاک می‌شوند!")


def test_survival_after_deploy():
    """تست بقای تصاویر بعد از deploy"""
    print_section("تست بقای تصاویر بعد از Deploy")
    
    # بررسی اینکه آیا تصاویر در دیتابیس ذخیره شده‌اند
    cache_count = ImageCache.objects.count()
    
    if cache_count > 0:
        from django.db.models import Q
        cache_with_base64 = ImageCache.objects.filter(image_data__isnull=False).count()
        cache_with_url = ImageCache.objects.filter(image_url__isnull=False).count()
        
        print(f"\n📊 آمار کش:")
        print(f"   کل کش‌ها: {cache_count}")
        print(f"   با Base64 (ذخیره در دیتابیس): {cache_with_base64}")
        print(f"   با URL (ذخیره در storage): {cache_with_url}")
        
        if cache_with_base64 > 0:
            print("\n✅ تصاویر در دیتابیس ذخیره شده‌اند!")
            print("   ✅ این تصاویر بعد از deploy پاک نمی‌شوند!")
            print("   ✅ می‌توانید از کش بازیابی کنید")
        elif cache_with_url > 0:
            print("\n⚠️ تصاویر فقط URL دارند (نه base64)")
            print("   ⚠️ اگر Cloudinary فعال باشد، مشکلی نیست")
            print("   ⚠️ اگر Cloudinary فعال نباشد، ممکن است بعد از deploy پاک شوند")
        else:
            print("\n❌ هیچ داده تصویری در کش وجود ندارد!")
    else:
        print("\n❌ هیچ تصویری کش نشده است!")


def main():
    """تابع اصلی"""
    print("\n" + "=" * 80)
    print("  تست کش تصاویر در Scalingo")
    print("=" * 80)
    
    # تست 1: بررسی storage
    test_storage_backend()
    
    # تست 2: بررسی Products و Sliders
    test_products_and_sliders()
    
    # تست 3: بررسی کش در دیتابیس
    cache_exists = test_image_cache_in_database()
    
    # تست 4: تست بقای تصاویر
    if cache_exists:
        test_survival_after_deploy()
    
    # خلاصه
    print_section("خلاصه و نتیجه")
    
    cache_count = ImageCache.objects.count()
    
    if cache_count > 0:
        from django.db.models import Q
        cache_with_base64 = ImageCache.objects.filter(image_data__isnull=False).count()
        
        print("\n✅ نتیجه:")
        print(f"   {cache_count} تصویر در دیتابیس کش شده است")
        
        if cache_with_base64 > 0:
            print(f"   {cache_with_base64} تصویر به صورت base64 در دیتابیس ذخیره شده")
            print("\n✅ تصاویر بعد از deploy پاک نمی‌شوند!")
            print("✅ می‌توانید با خیال راحت deploy کنید")
        else:
            print("\n⚠️ تصاویر فقط URL دارند")
            print("   برای اطمینان بیشتر، Cloudinary را فعال کنید")
    else:
        print("\n❌ هیچ تصویری کش نشده است!")
        print("   باید تصاویر را کش کنید:")
        print("   scalingo --app mywebsite run python manage.py shell < test_image_cache.py")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

