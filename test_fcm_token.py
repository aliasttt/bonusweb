"""
اسکریپت تست برای بررسی FCM Token و Push Notification
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.contrib.auth.models import User
from notifications.models import Device
from loyalty.models import Customer, Business, Wallet


def test_fcm_system():
    """تست سیستم FCM Token و Push Notification"""
    print("=" * 80)
    print("تست سیستم FCM Token و Push Notification")
    print("=" * 80)
    
    # بررسی Device ها
    devices = Device.objects.all()
    print(f"\n📱 تعداد Device های ثبت شده: {devices.count()}")
    
    if devices.count() > 0:
        print("\nنمونه Device ها:")
        for device in devices[:5]:
            print(f"  - User: {device.user.username}, Platform: {device.platform}, Token: {device.token[:50]}...")
    
    # بررسی Customer ها و Wallet ها
    customers = Customer.objects.all()
    print(f"\n👥 تعداد Customer ها: {customers.count()}")
    
    # بررسی اینکه آیا Customer ها Device دارند
    customers_with_devices = 0
    for customer in customers:
        if Device.objects.filter(user=customer.user).exists():
            customers_with_devices += 1
    
    print(f"✅ Customer هایی که Device دارند: {customers_with_devices}/{customers.count()}")
    
    # بررسی Business ها
    businesses = Business.objects.all()
    print(f"\n🏢 تعداد Business ها: {businesses.count()}")
    
    # برای هر Business، بررسی تعداد Customer ها و Device ها
    print("\n📊 آمار برای هر Business:")
    for business in businesses:
        wallets = Wallet.objects.filter(business=business)
        customer_user_ids = wallets.values_list('customer__user_id', flat=True).distinct()
        devices_count = Device.objects.filter(user_id__in=customer_user_ids).count()
        
        print(f"\n  Business: {business.name} (ID: {business.id})")
        print(f"    Wallets: {wallets.count()}")
        print(f"    Customers: {len(customer_user_ids)}")
        print(f"    Devices: {devices_count}")
    
    # بررسی Firebase Configuration
    print("\n" + "=" * 80)
    print("بررسی Firebase Configuration")
    print("=" * 80)
    
    from django.conf import settings
    
    firebase_creds_file = getattr(settings, 'FIREBASE_CREDENTIALS_FILE', '')
    firebase_creds_json = getattr(settings, 'FIREBASE_CREDENTIALS_JSON', '')
    firebase_creds_base64 = getattr(settings, 'FIREBASE_CREDENTIALS_BASE64', '')
    fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', '')
    
    print(f"\nFIREBASE_CREDENTIALS_FILE: {'SET' if firebase_creds_file else 'NOT SET'}")
    print(f"FIREBASE_CREDENTIALS_JSON: {'SET' if firebase_creds_json else 'NOT SET'}")
    print(f"FIREBASE_CREDENTIALS_BASE64: {'SET' if firebase_creds_base64 else 'NOT SET'}")
    print(f"FCM_SERVER_KEY: {'SET' if fcm_server_key else 'NOT SET'}")
    
    # بررسی Firebase Admin SDK
    try:
        import firebase_admin
        from firebase_admin import messaging
        
        if firebase_admin._apps:
            print("\n✅ Firebase Admin SDK initialized")
        else:
            print("\n⚠️ Firebase Admin SDK not initialized")
    except ImportError:
        print("\n⚠️ Firebase Admin SDK not installed")
    except Exception as e:
        print(f"\n⚠️ Firebase Admin SDK error: {e}")
    
    print("\n" + "=" * 80)
    print("خلاصه:")
    print("=" * 80)
    print(f"✅ API: POST /api/users/fcm-token")
    print(f"✅ Token Storage: Device model")
    print(f"✅ Send Notification: POST /api/notifications/send/")
    print(f"✅ Admin Panel: /partners/notifications/")
    
    if devices.count() > 0:
        print(f"\n✅ {devices.count()} Device ثبت شده است")
    else:
        print("\n⚠️ هیچ Device ثبت نشده است")
        print("   کاربران باید token خود را با POST /api/users/fcm-token ثبت کنند")
    
    if not (firebase_creds_file or firebase_creds_json or firebase_creds_base64):
        print("\n⚠️ Firebase credentials تنظیم نشده است!")
        print("   برای ارسال notification، باید Firebase credentials را تنظیم کنید")


if __name__ == "__main__":
    test_fcm_system()

