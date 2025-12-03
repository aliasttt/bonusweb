"""
اسکریپت برای تغییر points_balance از 0 به 200 برای همه کاربران
این یک تغییر موقت است
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from loyalty.models import Wallet

def update_points():
    """تغییر points_balance همه Wallet ها به 200"""
    print("=" * 80)
    print("تغییر points_balance همه Wallet ها به 200")
    print("=" * 80)
    
    # پیدا کردن همه Wallet ها
    all_wallets = Wallet.objects.all()
    total_count = all_wallets.count()
    
    print(f"\nتعداد کل Wallet ها: {total_count}")
    
    if total_count == 0:
        print("هیچ Wallet یافت نشد!")
        return
    
    # نمایش وضعیت فعلی
    print("\nوضعیت فعلی Wallet ها:")
    for wallet in all_wallets[:10]:
        print(f"  - Wallet ID {wallet.id}: Customer={wallet.customer}, Business={wallet.business.name}, Points={wallet.points_balance}")
    
    if total_count > 10:
        print(f"  ... و {total_count - 10} Wallet دیگر")
    
    # نمایش آمار
    wallets_with_zero = Wallet.objects.filter(points_balance=0).count()
    wallets_less_than_200 = Wallet.objects.filter(points_balance__lt=200).count()
    
    print(f"\nآمار:")
    print(f"  Wallet هایی با points_balance = 0: {wallets_with_zero}")
    print(f"  Wallet هایی با points_balance < 200: {wallets_less_than_200}")
    
    # به‌روزرسانی همه Wallet ها به 200
    print(f"\n⚠️  به‌روزرسانی همه {total_count} Wallet به points_balance = 200...")
    
    updated = Wallet.objects.all().update(points_balance=200)
    
    print(f"\n✅ {updated} Wallet به‌روزرسانی شد!")
    print(f"   همه Wallet ها حالا points_balance = 200 دارند")
    
    # بررسی نتیجه
    wallets_with_200 = Wallet.objects.filter(points_balance=200).count()
    print(f"\nتعداد Wallet هایی با points_balance = 200: {wallets_with_200}")
    
    print("\n" + "=" * 80)
    print("انجام شد!")
    print("=" * 80)


if __name__ == "__main__":
    update_points()

