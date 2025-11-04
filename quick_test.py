"""تست سریع endpoint ثبت نام"""
import requests
import json

url = "http://127.0.0.1:8080/api/accounts/register/"

data = {
    "username": "testuser123",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "email": "test@example.com",
    "phone": "09123456789",
    "first_name": "تست",
    "last_name": "کاربر"
}

print("=" * 60)
print("🧪 تست ثبت نام")
print("=" * 60)
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
print()

try:
    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.content:
        response_data = response.json()
        print("Response:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        print()
        
        # بررسی توکن
        has_access = "access" in response_data
        has_refresh = "refresh" in response_data
        
        print("=" * 60)
        print("📊 نتیجه:")
        print("=" * 60)
        print(f"✅ Access Token: {'دارد' if has_access else '❌ ندارد'}")
        print(f"✅ Refresh Token: {'دارد' if has_refresh else '❌ ندارد'}")
        
        if has_access and has_refresh:
            print()
            print("🎉 موفق! توکن‌ها در پاسخ وجود دارند!")
            print(f"Access Token: {response_data['access'][:50]}...")
            print(f"Refresh Token: {response_data['refresh'][:50]}...")
        else:
            print()
            print("❌ خطا! توکن‌ها در پاسخ وجود ندارند!")
    else:
        print("❌ پاسخ خالی است!")
        
except Exception as e:
    print(f"❌ خطا: {str(e)}")

