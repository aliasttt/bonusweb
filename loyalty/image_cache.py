"""
سیستم مدیریت کش تصاویر
این ماژول توابعی برای ذخیره و بازیابی تصاویر در کش دیتابیس فراهم می‌کند
"""

import base64
from typing import Optional, Tuple
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from .models import ImageCache, Product, Slider


class ImageCacheManager:
    """مدیریت کش تصاویر"""
    
    MAX_BASE64_SIZE = 5 * 1024 * 1024  # 5MB - حداکثر حجم برای ذخیره base64
    
    @staticmethod
    def cache_image(
        model_instance,
        image_field_name: str = 'image',
        store_base64: bool = True,
        max_base64_size: int = None
    ) -> Optional[ImageCache]:
        """
        کش کردن تصویر یک مدل
        
        Args:
            model_instance: نمونه مدل (مثلاً Product یا Slider)
            image_field_name: نام فیلد تصویر (پیش‌فرض: 'image')
            store_base64: آیا تصویر را به صورت base64 ذخیره کنیم؟
            max_base64_size: حداکثر حجم برای ذخیره base64 (پیش‌فرض: 5MB)
        
        Returns:
            ImageCache instance یا None در صورت خطا
        """
        if not model_instance or not hasattr(model_instance, image_field_name):
            return None
        
        image_field = getattr(model_instance, image_field_name)
        if not image_field:
            return None
        
        try:
            content_type = f"{model_instance._meta.app_label}.{model_instance._meta.model_name}"
            object_id = model_instance.pk
            original_path = image_field.name if hasattr(image_field, 'name') else str(image_field)
            
            # بررسی اینکه آیا قبلاً کش شده است
            cache, created = ImageCache.objects.get_or_create(
                content_type=content_type,
                object_id=object_id,
                original_path=original_path,
                defaults={}
            )
            
            # اگر قبلاً کش شده و داده دارد، نیازی به ذخیره مجدد نیست
            if not created and cache.has_data:
                return cache
            
            # دریافت URL تصویر
            image_url = None
            try:
                if hasattr(image_field, 'url'):
                    image_url = image_field.url
            except Exception:
                pass
            
            # ذخیره base64 (فقط برای تصاویر کوچک)
            image_data = None
            content_type_header = None
            
            if store_base64:
                max_size = max_base64_size or ImageCacheManager.MAX_BASE64_SIZE
                try:
                    # خواندن فایل
                    if hasattr(image_field, 'read'):
                        image_field.seek(0)
                        file_data = image_field.read()
                        file_size = len(file_data)
                        
                        if file_size <= max_size:
                            # تبدیل به base64
                            image_data = base64.b64encode(file_data).decode('utf-8')
                            content_type_header = getattr(image_field, 'content_type', 'image/jpeg')
                            
                            # بازگشت به ابتدای فایل
                            image_field.seek(0)
                        else:
                            # فایل خیلی بزرگ است، فقط URL را ذخیره می‌کنیم
                            pass
                except Exception as e:
                    # در صورت خطا، فقط URL را ذخیره می‌کنیم
                    pass
            
            # به‌روزرسانی کش
            cache.image_url = image_url
            cache.image_data = image_data
            cache.content_type_header = content_type_header
            if hasattr(image_field, 'size'):
                cache.file_size = image_field.size
            
            cache.save()
            return cache
            
        except Exception as e:
            print(f"خطا در کش کردن تصویر: {e}")
            return None
    
    @staticmethod
    def get_cached_image(
        model_instance,
        image_field_name: str = 'image'
    ) -> Optional[ImageCache]:
        """
        بازیابی تصویر کش شده
        
        Args:
            model_instance: نمونه مدل
            image_field_name: نام فیلد تصویر
        
        Returns:
            ImageCache instance یا None
        """
        if not model_instance or not hasattr(model_instance, image_field_name):
            return None
        
        image_field = getattr(model_instance, image_field_name)
        if not image_field:
            return None
        
        try:
            content_type = f"{model_instance._meta.app_label}.{model_instance._meta.model_name}"
            object_id = model_instance.pk
            original_path = image_field.name if hasattr(image_field, 'name') else str(image_field)
            
            cache = ImageCache.objects.filter(
                content_type=content_type,
                object_id=object_id,
                original_path=original_path
            ).first()
            
            if cache:
                # به‌روزرسانی زمان دسترسی
                from django.utils import timezone
                cache.last_accessed = timezone.now()
                cache.save(update_fields=['last_accessed'])
            
            return cache
            
        except Exception:
            return None
    
    @staticmethod
    def cache_all_images():
        """کش کردن همه تصاویر موجود"""
        cached_count = 0
        error_count = 0
        
        # کش کردن تصاویر Products
        products = Product.objects.filter(image__isnull=False).exclude(image='')
        for product in products:
            cache = ImageCacheManager.cache_image(product)
            if cache:
                cached_count += 1
            else:
                error_count += 1
        
        # کش کردن تصاویر Sliders
        sliders = Slider.objects.filter(image__isnull=False).exclude(image='')
        for slider in sliders:
            cache = ImageCacheManager.cache_image(slider)
            if cache:
                cached_count += 1
            else:
                error_count += 1
        
        return {
            'cached': cached_count,
            'errors': error_count,
            'total': cached_count + error_count
        }
    
    @staticmethod
    def restore_image_from_cache(model_instance, image_field_name: str = 'image') -> bool:
        """
        بازیابی تصویر از کش در صورت پاک شدن فایل اصلی
        
        Args:
            model_instance: نمونه مدل
            image_field_name: نام فیلد تصویر
        
        Returns:
            True اگر موفق بود، False در غیر این صورت
        """
        cache = ImageCacheManager.get_cached_image(model_instance, image_field_name)
        if not cache or not cache.has_data:
            return False
        
        try:
            image_field = getattr(model_instance, image_field_name)
            
            # اگر فایل وجود دارد، نیازی به بازیابی نیست
            if image_field and hasattr(image_field, 'name'):
                if default_storage.exists(image_field.name):
                    return True
            
            # بازیابی از base64
            if cache.image_data:
                try:
                    image_bytes = base64.b64decode(cache.image_data)
                    content_file = ContentFile(image_bytes, name=cache.original_path)
                    setattr(model_instance, image_field_name, content_file)
                    model_instance.save(update_fields=[image_field_name])
                    return True
                except Exception as e:
                    print(f"خطا در بازیابی از base64: {e}")
            
            # اگر base64 نبود، URL را برمی‌گردانیم (نیازی به ذخیره مجدد نیست)
            return False
            
        except Exception as e:
            print(f"خطا در بازیابی تصویر: {e}")
            return False
    
    @staticmethod
    def cleanup_old_cache(days: int = 90):
        """
        پاک کردن کش‌های قدیمی که دیگر استفاده نمی‌شوند
        
        Args:
            days: تعداد روزهای عدم دسترسی برای پاک کردن
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = ImageCache.objects.filter(last_accessed__lt=cutoff_date).delete()[0]
        return deleted_count

