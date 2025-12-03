"""
اسکریپت دیباگ کامل برای بررسی وضعیت تصاویر و storage
این اسکریپت بررسی می‌کند که:
1. آیا تصاویر در دیتابیس ذخیره شده‌اند؟
2. آیا فایل‌های فیزیکی وجود دارند؟
3. آیا Cloudinary فعال است؟
4. آیا تصاویر در session هستند؟
5. وضعیت storage backend چیست؟

Usage:
    python manage.py shell < debug_image_storage.py
    OR
    python debug_image_storage.py
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.sessions.models import Session
from loyalty.models import Product, Slider, Business
import base64


def print_section(title):
    """چاپ عنوان بخش"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check_storage_backend():
    """بررسی storage backend"""
    print_section("1. بررسی Storage Backend")
    
    print(f"Storage Class: {type(default_storage).__name__}")
    print(f"Storage Module: {type(default_storage).__module__}")
    print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
    print(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")
    print(f"MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'Not set')}")
    
    # بررسی Cloudinary
    use_cloudinary = os.environ.get('USE_CLOUDINARY', '0') == '1'
    print(f"\nUSE_CLOUDINARY env: {use_cloudinary}")
    
    if 'cloudinary' in str(getattr(settings, 'DEFAULT_FILE_STORAGE', '')).lower():
        print("✅ Cloudinary فعال است - فایل‌ها در cloud ذخیره می‌شوند")
        try:
            import cloudinary
            print(f"Cloud Name: {cloudinary.config().cloud_name}")
            print(f"API Key: {'SET' if cloudinary.config().api_key else 'NOT SET'}")
        except Exception as e:
            print(f"⚠️ خطا در اتصال به Cloudinary: {e}")
    else:
        print("⚠️ Cloudinary فعال نیست - فایل‌ها در فایل‌سیستم محلی ذخیره می‌شوند")
        print("⚠️ در Scalingo این فایل‌ها بعد از هر deploy پاک می‌شوند!")


def check_database_images():
    """بررسی تصاویر در دیتابیس"""
    print_section("2. بررسی تصاویر در دیتابیس")
    
    # بررسی Products
    products = Product.objects.filter(image__isnull=False).exclude(image='')
    print(f"\n📦 Products با تصویر: {products.count()}")
    
    product_stats = {
        'total': products.count(),
        'exists': 0,
        'missing': 0,
        'details': []
    }
    
    for product in products[:10]:  # فقط 10 تا اول
        try:
            exists = default_storage.exists(product.image.name) if product.image.name else False
            if exists:
                product_stats['exists'] += 1
                status = "✅"
            else:
                product_stats['missing'] += 1
                status = "❌"
            
            product_stats['details'].append({
                'id': product.id,
                'title': product.title,
                'image_path': product.image.name if product.image else None,
                'exists': exists,
                'url': product.image.url if product.image else None
            })
            
            print(f"{status} Product ID {product.id}: {product.title}")
            print(f"   Path: {product.image.name if product.image else 'None'}")
            print(f"   URL: {product.image.url if product.image else 'None'}")
            print(f"   Exists: {exists}")
        except Exception as e:
            print(f"❌ خطا در بررسی Product ID {product.id}: {e}")
            product_stats['missing'] += 1
    
    if products.count() > 10:
        print(f"\n... و {products.count() - 10} محصول دیگر")
    
    # بررسی Sliders
    sliders = Slider.objects.filter(image__isnull=False).exclude(image='')
    print(f"\n🖼️ Sliders با تصویر: {sliders.count()}")
    
    slider_stats = {
        'total': sliders.count(),
        'exists': 0,
        'missing': 0,
        'details': []
    }
    
    for slider in sliders[:10]:  # فقط 10 تا اول
        try:
            exists = default_storage.exists(slider.image.name) if slider.image.name else False
            if exists:
                slider_stats['exists'] += 1
                status = "✅"
            else:
                slider_stats['missing'] += 1
                status = "❌"
            
            slider_stats['details'].append({
                'id': slider.id,
                'store': slider.store,
                'image_path': slider.image.name if slider.image else None,
                'exists': exists,
                'url': slider.image.url if slider.image else None
            })
            
            print(f"{status} Slider ID {slider.id}: {slider.store}")
            print(f"   Path: {slider.image.name if slider.image else 'None'}")
            print(f"   URL: {slider.image.url if slider.image else 'None'}")
            print(f"   Exists: {exists}")
        except Exception as e:
            print(f"❌ خطا در بررسی Slider ID {slider.id}: {e}")
            slider_stats['missing'] += 1
    
    if sliders.count() > 10:
        print(f"\n... و {sliders.count() - 10} اسلایدر دیگر")
    
    return {
        'products': product_stats,
        'sliders': slider_stats
    }


def check_sessions():
    """بررسی session ها برای تصاویر"""
    print_section("3. بررسی Session ها")
    
    sessions = Session.objects.all()
    print(f"تعداد Session های فعال: {sessions.count()}")
    
    image_in_sessions = 0
    for session in sessions[:5]:  # فقط 5 تا اول
        try:
            session_data = session.get_decoded()
            # بررسی وجود تصاویر در session
            has_images = any('image' in str(key).lower() or 'upload' in str(key).lower() 
                           for key in session_data.keys())
            if has_images:
                image_in_sessions += 1
                print(f"Session {session.session_key[:20]}... دارای داده‌های تصویر")
        except Exception as e:
            pass
    
    print(f"\n⚠️ توجه: تصاویر معمولاً در session ذخیره نمی‌شوند")
    print(f"   تصاویر باید در دیتابیس (مدل‌ها) و storage ذخیره شوند")


def check_image_cache():
    """بررسی کش تصاویر در دیتابیس"""
    print_section("4. بررسی Image Cache")
    
    try:
        from loyalty.models import ImageCache
        
        cached_images = ImageCache.objects.all()
        print(f"تعداد تصاویر در کش: {cached_images.count()}")
        
        if cached_images.count() > 0:
            print("\nنمونه تصاویر کش شده:")
            for img_cache in cached_images[:5]:
                print(f"  - ID {img_cache.id}: {img_cache.original_path}")
                print(f"    Model: {img_cache.content_type}")
                print(f"    Created: {img_cache.created_at}")
                print(f"    Has Data: {'Yes' if img_cache.image_data else 'No'}")
                print(f"    Has URL: {'Yes' if img_cache.image_url else 'No'}")
        else:
            print("⚠️ هیچ تصویری در کش وجود ندارد")
            print("   سیستم کش هنوز فعال نشده است")
            
    except ImportError:
        print("⚠️ مدل ImageCache وجود ندارد")
        print("   باید migration را اجرا کنید")


def generate_report():
    """تولید گزارش کامل"""
    print_section("گزارش کامل")
    
    check_storage_backend()
    db_stats = check_database_images()
    check_sessions()
    check_image_cache()
    
    # خلاصه
    print_section("خلاصه و توصیه‌ها")
    
    total_images = db_stats['products']['total'] + db_stats['sliders']['total']
    total_missing = db_stats['products']['missing'] + db_stats['sliders']['missing']
    
    print(f"📊 آمار کلی:")
    print(f"   کل تصاویر در دیتابیس: {total_images}")
    print(f"   تصاویر موجود: {total_images - total_missing}")
    print(f"   تصاویر گم شده: {total_missing}")
    
    if total_missing > 0:
        print(f"\n⚠️ مشکل شناسایی شد!")
        print(f"   {total_missing} تصویر در دیتابیس ثبت شده اما فایل فیزیکی وجود ندارد")
        print(f"\n💡 راه حل‌ها:")
        print(f"   1. فعال کردن Cloudinary برای ذخیره دائمی")
        print(f"   2. استفاده از سیستم کش برای ذخیره در دیتابیس")
        print(f"   3. آپلود مجدد تصاویر گم شده")
    else:
        print(f"\n✅ همه تصاویر موجود هستند!")
    
    # بررسی Cloudinary
    use_cloudinary = os.environ.get('USE_CLOUDINARY', '0') == '1'
    if not use_cloudinary:
        print(f"\n⚠️ هشدار مهم:")
        print(f"   Cloudinary فعال نیست!")
        print(f"   در Scalingo، فایل‌ها بعد از هر deploy پاک می‌شوند")
        print(f"   برای فعال کردن: USE_CLOUDINARY=1 را تنظیم کنید")


if __name__ == "__main__":
    generate_report()

