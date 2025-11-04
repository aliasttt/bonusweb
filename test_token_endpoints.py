"""
اسکریپت تست کامل برای همه endpoint های احراز هویت و توکن
این اسکریپت بررسی می‌کند که آیا همه endpoint ها توکن برمی‌گردانند یا نه
"""
import requests
import json
from typing import Dict, Optional

BASE_URL = "http://127.0.0.1:8080/api"

class TokenTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.test_username: Optional[str] = None
        self.test_password: Optional[str] = None
        self.test_results = []
    
    def log_result(self, endpoint: str, method: str, status_code: int, 
                   success: bool, has_token: bool, message: str = ""):
        """ثبت نتیجه تست"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "has_token": has_token,
            "message": message
        }
        self.test_results.append(result)
        
        status = "✅" if success and has_token else "❌" if not success else "⚠️"
        token_status = "✅ توکن دارد" if has_token else "❌ توکن ندارد"
        print(f"{status} {method} {endpoint}")
        print(f"   Status: {status_code} | {token_status}")
        if message:
            print(f"   Message: {message}")
        print()
    
    def test_register(self) -> bool:
        """تست endpoint ثبت نام - باید توکن برگرداند"""
        print("=" * 60)
        print("🔐 تست ثبت نام: POST /api/accounts/register/")
        print("=" * 60)
        
        import random
        import time
        
        username = f"testuser_{int(time.time())}_{random.randint(1000, 9999)}"
        email = f"{username}@example.com"
        password = "TestPass123!"
        phone = f"0912345{random.randint(1000, 9999)}"
        
        self.test_username = username
        self.test_password = password
        
        data = {
            "username": username,
            "email": email,
            "password": password,
            "password_confirm": password,
            "phone": phone,
            "first_name": "تست",
            "last_name": "کاربر"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/accounts/register/",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            response_data = response.json() if response.content else {}
            has_access = "access" in response_data
            has_refresh = "refresh" in response_data
            has_token = has_access and has_refresh
            
            if has_access:
                self.access_token = response_data["access"]
            if has_refresh:
                self.refresh_token = response_data["refresh"]
            
            success = response.status_code == 201 and has_token
            
            self.log_result(
                "/accounts/register/",
                "POST",
                response.status_code,
                success,
                has_token,
                f"access: {has_access}, refresh: {has_refresh}"
            )
            
            if has_token:
                print(f"✅ توکن‌ها دریافت شدند:")
                print(f"   Access Token: {self.access_token[:50]}...")
                print(f"   Refresh Token: {self.refresh_token[:50]}...")
            else:
                print(f"❌ توکن در پاسخ وجود ندارد!")
                print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            return success
            
        except Exception as e:
            self.log_result(
                "/accounts/register/",
                "POST",
                0,
                False,
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_login_accounts(self) -> bool:
        """تست endpoint لاگین در accounts - باید توکن برگرداند"""
        print("=" * 60)
        print("🔐 تست لاگین: POST /api/accounts/token/")
        print("=" * 60)
        
        if not self.test_username or not self.test_password:
            print("⚠️  ابتدا باید ثبت نام انجام شود")
            return False
        
        data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/accounts/token/",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            response_data = response.json() if response.content else {}
            has_access = "access" in response_data
            has_refresh = "refresh" in response_data
            has_token = has_access and has_refresh
            
            if has_access:
                self.access_token = response_data["access"]
            if has_refresh:
                self.refresh_token = response_data["refresh"]
            
            success = response.status_code == 200 and has_token
            
            self.log_result(
                "/accounts/token/",
                "POST",
                response.status_code,
                success,
                has_token,
                f"access: {has_access}, refresh: {has_refresh}"
            )
            
            if has_token:
                print(f"✅ توکن‌ها دریافت شدند:")
                print(f"   Access Token: {self.access_token[:50]}...")
                print(f"   Refresh Token: {self.refresh_token[:50]}...")
            else:
                print(f"❌ توکن در پاسخ وجود ندارد!")
                print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            return success
            
        except Exception as e:
            self.log_result(
                "/accounts/token/",
                "POST",
                0,
                False,
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_token_refresh_accounts(self) -> bool:
        """تست تازه‌سازی توکن در accounts - باید access token جدید برگرداند"""
        print("=" * 60)
        print("🔄 تست تازه‌سازی توکن: POST /api/accounts/token/refresh/")
        print("=" * 60)
        
        if not self.refresh_token:
            print("⚠️  ابتدا باید لاگین یا ثبت نام انجام شود")
            return False
        
        data = {
            "refresh": self.refresh_token
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/accounts/token/refresh/",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            response_data = response.json() if response.content else {}
            has_access = "access" in response_data
            has_token = has_access
            
            if has_access:
                self.access_token = response_data["access"]
                print(f"✅ توکن جدید دریافت شد:")
                print(f"   New Access Token: {self.access_token[:50]}...")
            
            success = response.status_code == 200 and has_token
            
            self.log_result(
                "/accounts/token/refresh/",
                "POST",
                response.status_code,
                success,
                has_token,
                f"access: {has_access}"
            )
            
            if not has_token:
                print(f"❌ توکن در پاسخ وجود ندارد!")
                print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            return success
            
        except Exception as e:
            self.log_result(
                "/accounts/token/refresh/",
                "POST",
                0,
                False,
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_login_loyalty(self) -> bool:
        """تست endpoint لاگین در loyalty - باید توکن برگرداند"""
        print("=" * 60)
        print("🔐 تست لاگین (Loyalty): POST /api/auth/token/")
        print("=" * 60)
        
        if not self.test_username or not self.test_password:
            print("⚠️  ابتدا باید ثبت نام انجام شود")
            return False
        
        data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/token/",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            response_data = response.json() if response.content else {}
            has_access = "access" in response_data
            has_refresh = "refresh" in response_data
            has_token = has_access and has_refresh
            
            success = response.status_code == 200 and has_token
            
            self.log_result(
                "/auth/token/",
                "POST",
                response.status_code,
                success,
                has_token,
                f"access: {has_access}, refresh: {has_refresh}"
            )
            
            if has_token:
                print(f"✅ توکن‌ها دریافت شدند:")
                print(f"   Access Token: {response_data.get('access', '')[:50]}...")
                print(f"   Refresh Token: {response_data.get('refresh', '')[:50]}...")
            else:
                print(f"❌ توکن در پاسخ وجود ندارد!")
                print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            return success
            
        except Exception as e:
            self.log_result(
                "/auth/token/",
                "POST",
                0,
                False,
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_token_refresh_loyalty(self) -> bool:
        """تست تازه‌سازی توکن در loyalty - باید access token جدید برگرداند"""
        print("=" * 60)
        print("🔄 تست تازه‌سازی توکن (Loyalty): POST /api/auth/refresh/")
        print("=" * 60)
        
        if not self.refresh_token:
            print("⚠️  ابتدا باید لاگین یا ثبت نام انجام شود")
            return False
        
        data = {
            "refresh": self.refresh_token
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/refresh/",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            response_data = response.json() if response.content else {}
            has_access = "access" in response_data
            has_token = has_access
            
            success = response.status_code == 200 and has_token
            
            self.log_result(
                "/auth/refresh/",
                "POST",
                response.status_code,
                success,
                has_token,
                f"access: {has_access}"
            )
            
            if has_token:
                print(f"✅ توکن جدید دریافت شد:")
                print(f"   New Access Token: {response_data.get('access', '')[:50]}...")
            else:
                print(f"❌ توکن در پاسخ وجود ندارد!")
                print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            return success
            
        except Exception as e:
            self.log_result(
                "/auth/refresh/",
                "POST",
                0,
                False,
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_me_endpoint(self) -> bool:
        """تست endpoint /me - باید با توکن کار کند"""
        print("=" * 60)
        print("👤 تست دریافت اطلاعات کاربر: GET /api/accounts/me/")
        print("=" * 60)
        
        if not self.access_token:
            print("⚠️  ابتدا باید لاگین یا ثبت نام انجام شود")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/accounts/me/",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            response_data = response.json() if response.content else {}
            success = response.status_code == 200
            
            self.log_result(
                "/accounts/me/",
                "GET",
                response.status_code,
                success,
                True,  # این endpoint توکن برنمی‌گرداند، اما با توکن کار می‌کند
                f"User authenticated: {success}"
            )
            
            if success:
                print(f"✅ احراز هویت موفق بود")
                print(f"   User: {response_data.get('user', {}).get('username', 'N/A')}")
            else:
                print(f"❌ احراز هویت ناموفق!")
                print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            return success
            
        except Exception as e:
            self.log_result(
                "/accounts/me/",
                "GET",
                0,
                False,
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """اجرای همه تست‌ها"""
        print("\n" + "=" * 60)
        print("🧪 تست کامل همه endpoint های احراز هویت و توکن")
        print("=" * 60)
        print()
        
        # 1. تست ثبت نام
        self.test_register()
        
        # 2. تست لاگین (accounts)
        self.test_login_accounts()
        
        # 3. تست تازه‌سازی توکن (accounts)
        self.test_token_refresh_accounts()
        
        # 4. تست لاگین (loyalty)
        self.test_login_loyalty()
        
        # 5. تست تازه‌سازی توکن (loyalty)
        self.test_token_refresh_loyalty()
        
        # 6. تست endpoint /me
        self.test_me_endpoint()
        
        # خلاصه نتایج
        print("\n" + "=" * 60)
        print("📊 خلاصه نتایج")
        print("=" * 60)
        
        total = len(self.test_results)
        token_tests = [r for r in self.test_results if r["has_token"]]
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        print(f"تعداد کل تست‌ها: {total}")
        print(f"✅ موفق: {passed}")
        print(f"❌ ناموفق: {failed}")
        print(f"تست‌های با توکن: {len(token_tests)}/{total}")
        
        print("\n📋 جزئیات نتایج:")
        for result in self.test_results:
            status = "✅" if result["success"] and result["has_token"] else "❌" if not result["success"] else "⚠️"
            token_status = "✅ توکن دارد" if result["has_token"] else "❌ توکن ندارد"
            print(f"{status} {result['method']} {result['endpoint']} - {result['status_code']} - {token_status}")
        
        # بررسی مشکلات
        print("\n🔍 بررسی مشکلات:")
        issues = []
        for result in self.test_results:
            if result["endpoint"] in ["/accounts/register/", "/accounts/token/", 
                                      "/accounts/token/refresh/", "/auth/token/", 
                                      "/auth/refresh/"]:
                if not result["has_token"]:
                    issues.append(f"{result['endpoint']} توکن برنمی‌گرداند")
                if not result["success"]:
                    issues.append(f"{result['endpoint']} با خطا مواجه شد: {result['message']}")
        
        if issues:
            print("❌ مشکلات پیدا شده:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ همه endpoint ها به درستی توکن برمی‌گردانند!")


if __name__ == "__main__":
    import sys
    
    # بررسی اتصال به سرور
    try:
        response = requests.get(BASE_URL.replace("/api", ""), timeout=2)
    except:
        print("⚠️  هشدار: نمی‌توان به سرور متصل شد. مطمئن شوید که سرور Django در حال اجرا است:")
        print("   python manage.py runserver")
        print("\nادامه تست‌ها...")
        print()
    
    tester = TokenTester()
    tester.run_all_tests()

