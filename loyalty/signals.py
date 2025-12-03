"""
Signal handlers for automatic image caching
این signal ها به صورت خودکار تصاویر را در کش ذخیره می‌کنند
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Product, Slider, ImageCache
from .image_cache import ImageCacheManager


@receiver(post_save, sender=Product)
def cache_product_image(sender, instance, created, **kwargs):
    """کش کردن تصویر Product بعد از ذخیره"""
    if instance.image:
        try:
            ImageCacheManager.cache_image(instance, image_field_name='image')
        except Exception as e:
            # در صورت خطا، لاگ می‌کنیم اما خطا را بالا نمی‌فرستیم
            print(f"خطا در کش کردن تصویر Product ID {instance.id}: {e}")


@receiver(post_save, sender=Slider)
def cache_slider_image(sender, instance, created, **kwargs):
    """کش کردن تصویر Slider بعد از ذخیره"""
    if instance.image:
        try:
            ImageCacheManager.cache_image(instance, image_field_name='image')
        except Exception as e:
            # در صورت خطا، لاگ می‌کنیم اما خطا را بالا نمی‌فرستیم
            print(f"خطا در کش کردن تصویر Slider ID {instance.id}: {e}")


@receiver(pre_delete, sender=Product)
def cleanup_product_image_cache(sender, instance, **kwargs):
    """پاک کردن کش تصویر Product قبل از حذف"""
    try:
        ImageCache.objects.filter(
            content_type='loyalty.product',
            object_id=instance.pk
        ).delete()
    except Exception:
        pass


@receiver(pre_delete, sender=Slider)
def cleanup_slider_image_cache(sender, instance, **kwargs):
    """پاک کردن کش تصویر Slider قبل از حذف"""
    try:
        ImageCache.objects.filter(
            content_type='loyalty.slider',
            object_id=instance.pk
        ).delete()
    except Exception:
        pass

