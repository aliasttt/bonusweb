"""
Script to verify Cloudinary is properly configured and active.
Run this in Scalingo shell: python manage.py shell < check_cloudinary.py
"""

from django.conf import settings
import os

print("=" * 60)
print("Cloudinary Configuration Check")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   USE_CLOUDINARY: {os.environ.get('USE_CLOUDINARY', 'NOT SET')}")
print(f"   CLOUDINARY_CLOUD_NAME: {os.environ.get('CLOUDINARY_CLOUD_NAME', 'NOT SET')}")
print(f"   CLOUDINARY_API_KEY: {'SET' if os.environ.get('CLOUDINARY_API_KEY') else 'NOT SET'}")
print(f"   CLOUDINARY_API_SECRET: {'SET' if os.environ.get('CLOUDINARY_API_SECRET') else 'NOT SET'}")

# Check Django settings
print("\n2. Django Settings:")
print(f"   DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
print(f"   MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'NOT SET')}")
print(f"   MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'NOT SET')}")

# Check if Cloudinary is actually being used
print("\n3. Storage Backend Check:")
try:
    from django.core.files.storage import default_storage
    storage_class = type(default_storage).__name__
    storage_module = type(default_storage).__module__
    print(f"   Active Storage: {storage_module}.{storage_class}")
    
    if 'cloudinary' in storage_module.lower():
        print("   ✅ Cloudinary is ACTIVE - Files will be stored permanently!")
    else:
        print("   ⚠️  Cloudinary is NOT active - Files will be lost on restart!")
except Exception as e:
    print(f"   ❌ Error checking storage: {e}")

# Test Cloudinary connection
print("\n4. Cloudinary Connection Test:")
try:
    import cloudinary
    import cloudinary.api
    
    # Try to ping Cloudinary
    result = cloudinary.api.ping()
    print(f"   ✅ Cloudinary connection: SUCCESS")
    print(f"   Cloud Name: {cloudinary.config().cloud_name}")
except ImportError:
    print("   ❌ Cloudinary package not installed")
except Exception as e:
    print(f"   ⚠️  Cloudinary connection error: {e}")

print("\n" + "=" * 60)
print("Summary:")
if 'cloudinary' in str(getattr(settings, 'DEFAULT_FILE_STORAGE', '')).lower():
    print("✅ Cloudinary is configured correctly!")
    print("✅ New uploads will be stored permanently in Cloudinary")
    print("✅ Files will NOT be lost after restart/deployment")
else:
    print("❌ Cloudinary is NOT configured!")
    print("⚠️  Files will be lost after restart/deployment")
print("=" * 60)



