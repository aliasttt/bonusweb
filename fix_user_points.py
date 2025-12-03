"""
اسکریپت برای ایجاد Wallet با points_balance=200 برای کاربرانی که Wallet ندارند
یا به‌روزرسانی Wallet های موجود به 200
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from loyalty.models import Wallet, Customer, Business
from django.contrib.auth.models import User


def fix_user_points():
    """ایجاد یا به‌روزرسانی Wallet برای همه کاربران"""
    print("=" * 80)
    print("ایجاد/به‌روزرسانی Wallet برای همه کاربران")
    print("=" * 80)
    
    # دریافت همه Business ها
    businesses = Business.objects.all()
    print(f"\nتعداد Business ها: {businesses.count()}")
    
    # دریافت همه Customer ها
    customers = Customer.objects.all()
    print(f"تعداد Customer ها: {customers.count()}")
    
    total_created = 0
    total_updated = 0
    
    # برای هر Business و Customer، Wallet ایجاد یا به‌روزرسانی کن
    for business in businesses:
        print(f"\n📦 Business: {business.name} (ID: {business.id})")
        
        for customer in customers:
            wallet, created = Wallet.objects.get_or_create(
                customer=customer,
                business=business,
                defaults={
                    'points_balance': 200,
                    'reward_point_cost': business.reward_point_cost or 100
                }
            )
            
            if created:
                total_created += 1
                print(f"  ✅ ایجاد شد: Customer={customer.user.username}, Points=200")
            else:
                # اگر Wallet وجود داشت، points_balance را به 200 تغییر بده
                if wallet.points_balance != 200:
                    old_points = wallet.points_balance
                    wallet.points_balance = 200
                    wallet.reward_point_cost = business.reward_point_cost or 100
                    wallet.save(update_fields=['points_balance', 'reward_point_cost'])
                    total_updated += 1
                    print(f"  🔄 به‌روزرسانی شد: Customer={customer.user.username}, {old_points} → 200")
                else:
                    print(f"  ✓ قبلاً 200 است: Customer={customer.user.username}")
    
    print("\n" + "=" * 80)
    print("خلاصه:")
    print("=" * 80)
    print(f"✅ {total_created} Wallet جدید ایجاد شد")
    print(f"🔄 {total_updated} Wallet به‌روزرسانی شد")
    
    # بررسی نتیجه
    wallets_with_200 = Wallet.objects.filter(points_balance=200).count()
    total_wallets = Wallet.objects.count()
    print(f"\n📊 آمار نهایی:")
    print(f"   کل Wallet ها: {total_wallets}")
    print(f"   Wallet های با points_balance=200: {wallets_with_200}")
    
    if wallets_with_200 == total_wallets:
        print("\n✅ همه Wallet ها حالا points_balance=200 دارند!")
    else:
        wallets_not_200 = Wallet.objects.exclude(points_balance=200)
        print(f"\n⚠️ {wallets_not_200.count()} Wallet هنوز 200 نیست:")
        for w in wallets_not_200[:5]:
            print(f"   - Wallet ID {w.id}: Customer={w.customer.user.username}, Business={w.business.name}, Points={w.points_balance}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    fix_user_points()

