"""
اسکریپت برای رفع مشکل total_points = 0 در API
این اسکریپت همه wallets با points_balance = 0 را به 200 تنظیم می‌کند
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from loyalty.models import Wallet, Customer, Business
from django.contrib.auth.models import User
from django.db.models import Sum

def fix_total_points():
    """تنظیم همه wallets با points_balance = 0 به 200"""
    print("=" * 80)
    print("رفع مشکل total_points = 0")
    print("=" * 80)
    
    # بررسی همه customers
    customers = Customer.objects.all()
    print(f"\nتعداد Customers: {customers.count()}")
    
    total_fixed = 0
    total_created = 0
    
    for customer in customers:
        wallets = Wallet.objects.filter(customer=customer)
        total_points = sum(w.points_balance for w in wallets) or 0
        
        print(f"\nCustomer: {customer.user.username} (ID: {customer.id})")
        print(f"  Wallets: {wallets.count()}")
        print(f"  Total points: {total_points}")
        
        if total_points == 0:
            if wallets.exists():
                # اگر wallets وجود دارند اما همه 0 هستند
                zero_wallets = wallets.filter(points_balance=0)
                if zero_wallets.exists():
                    print(f"  ⚠️  {zero_wallets.count()} wallet با points_balance = 0 پیدا شد")
                    zero_wallets.update(points_balance=200)
                    total_fixed += zero_wallets.count()
                    print(f"  ✅ {zero_wallets.count()} wallet به 200 تنظیم شد")
            else:
                # اگر هیچ wallet وجود ندارد
                print(f"  ⚠️  هیچ wallet وجود ندارد")
                first_business = Business.objects.first()
                if first_business:
                    Wallet.objects.create(
                        customer=customer,
                        business=first_business,
                        points_balance=200,
                        reward_point_cost=first_business.reward_point_cost or 100
                    )
                    total_created += 1
                    print(f"  ✅ یک wallet جدید با 200 points ایجاد شد")
        
        # دوباره total_points را محاسبه کن
        wallets = Wallet.objects.filter(customer=customer)
        total_points = sum(w.points_balance for w in wallets) or 0
        print(f"  📊 Total points بعد از fix: {total_points}")
    
    print("\n" + "=" * 80)
    print("خلاصه:")
    print("=" * 80)
    print(f"✅ {total_fixed} wallet به 200 تنظیم شد")
    print(f"✅ {total_created} wallet جدید ایجاد شد")
    
    # بررسی نهایی
    print("\nبررسی نهایی:")
    all_customers = Customer.objects.all()
    for customer in all_customers:
        wallets = Wallet.objects.filter(customer=customer)
        total_points = sum(w.points_balance for w in wallets) or 0
        if total_points == 0:
            print(f"⚠️  Customer {customer.user.username} هنوز total_points = 0 دارد!")
        else:
            print(f"✅ Customer {customer.user.username}: {total_points} points")

if __name__ == "__main__":
    fix_total_points()

