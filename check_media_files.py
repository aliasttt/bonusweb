"""
Script to check media files in database and verify if they exist in storage.
This helps diagnose missing media files after deployment.

Usage:
    python manage.py shell < check_media_files.py
    OR
    python check_media_files.py (if run as standalone script)
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.conf import settings
from loyalty.models import Product, Slider


def check_file_exists(file_field):
    """Check if a file exists in storage"""
    if not file_field:
        return False, "No file"
    
    try:
        # Try to access the file
        if hasattr(file_field, 'storage'):
            # For Cloudinary or other storage backends
            return file_field.storage.exists(file_field.name), "Exists in storage"
        else:
            # For local file storage
            file_path = file_field.path if hasattr(file_field, 'path') else None
            if file_path and os.path.exists(file_path):
                return True, "Exists locally"
            return False, f"File not found at: {file_path}"
    except Exception as e:
        return False, f"Error checking file: {str(e)}"


def check_media_files():
    """Check all media files in database"""
    print("=" * 60)
    print("MEDIA FILES CHECK")
    print("=" * 60)
    print(f"Storage Backend: {settings.DEFAULT_FILE_STORAGE if hasattr(settings, 'DEFAULT_FILE_STORAGE') else 'Default (local)'}")
    print(f"MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'Not set')}")
    print(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")
    print()
    
    # Check Products
    print("PRODUCTS:")
    print("-" * 60)
    products = Product.objects.filter(image__isnull=False).exclude(image='')
    print(f"Total products with images: {products.count()}")
    
    missing_count = 0
    for product in products:
        exists, message = check_file_exists(product.image)
        status = "✓" if exists else "✗"
        print(f"{status} Product ID {product.id} ({product.title}): {product.image.name}")
        if not exists:
            print(f"  → {message}")
            missing_count += 1
    
    print(f"\nMissing files: {missing_count}/{products.count()}")
    print()
    
    # Check Sliders
    print("SLIDERS:")
    print("-" * 60)
    sliders = Slider.objects.filter(image__isnull=False).exclude(image='')
    print(f"Total sliders with images: {sliders.count()}")
    
    missing_slider_count = 0
    for slider in sliders:
        exists, message = check_file_exists(slider.image)
        status = "✓" if exists else "✗"
        print(f"{status} Slider ID {slider.id} ({slider.store}): {slider.image.name}")
        if not exists:
            print(f"  → {message}")
            missing_slider_count += 1
    
    print(f"\nMissing files: {missing_slider_count}/{sliders.count()}")
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_files = products.count() + sliders.count()
    total_missing = missing_count + missing_slider_count
    print(f"Total files in database: {total_files}")
    print(f"Missing files: {total_missing}")
    print(f"Available files: {total_files - total_missing}")
    
    if total_missing > 0:
        print("\n⚠️  WARNING: Some files are missing!")
        print("   This usually happens when:")
        print("   1. Files were uploaded before enabling Cloudinary")
        print("   2. Files were lost during Scalingo deployment (ephemeral filesystem)")
        print("   3. Files need to be re-uploaded")
        print("\n   Solution: Re-upload the missing images through the admin panel.")
    else:
        print("\n✓ All files are available!")
    
    print("=" * 60)


if __name__ == "__main__":
    check_media_files()

