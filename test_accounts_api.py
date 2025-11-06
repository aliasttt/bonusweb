"""
Test script for Accounts API endpoints
Tests: sendMobile, register, login, and refresh token
"""

import requests
import json

# Base URL - change this to your server URL
BASE_URL = "https://mywebsite.osc-fr1.scalingo.io/api/accounts"
# For local testing, use: BASE_URL = "http://localhost:8000/api/accounts"

def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")


def test_send_mobile():
    """Test sendMobile endpoint"""
    print("\n🔍 Testing sendMobile API...")
    
    # Test with a phone number
    phone_number = "09123456789"
    
    response = requests.post(
        f"{BASE_URL}/sendMobile/",
        json={"number": phone_number},
        headers={"Content-Type": "application/json"}
    )
    
    print_response("sendMobile Response", response)
    
    if response.status_code == 200:
        print("✅ User exists - should go to LOGIN")
        return {"exists": True, "phone": phone_number}
    elif response.status_code == 201:
        print("✅ User doesn't exist - should go to REGISTER")
        return {"exists": False, "phone": phone_number}
    else:
        print("❌ Error in sendMobile")
        return None


def test_register():
    """Test register endpoint"""
    print("\n📝 Testing Register API...")
    
    # Test data
    register_data = {
        "number": "09123456789",
        "name": "علی احمدی",
        "password": "testpass123",
        "confirmPassword": "testpass123",
        "favorit": ["sports", "music", "technology"]
    }
    
    response = requests.post(
        f"{BASE_URL}/register/",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response("Register Response", response)
    
    if response.status_code == 201:
        data = response.json()
        if "access" in data and "refresh" in data:
            print("✅ Register successful - Tokens received!")
            print(f"   Access Token: {data['access'][:50]}...")
            print(f"   Refresh Token: {data['refresh'][:50]}...")
            return data
        else:
            print("❌ Register successful but NO TOKENS!")
            return None
    else:
        print("❌ Register failed")
        return None


def test_login():
    """Test login endpoint"""
    print("\n🔐 Testing Login API...")
    
    # Test data
    login_data = {
        "number": "09123456789",
        "password": "testpass123"
    }
    
    response = requests.post(
        f"{BASE_URL}/login/",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response("Login Response", response)
    
    if response.status_code == 200:
        data = response.json()
        if "access" in data and "refresh" in data:
            print("✅ Login successful - Tokens received!")
            print(f"   Access Token: {data['access'][:50]}...")
            print(f"   Refresh Token: {data['refresh'][:50]}...")
            return data
        else:
            print("❌ Login successful but NO TOKENS!")
            return None
    else:
        print("❌ Login failed")
        return None


def test_refresh_token(refresh_token):
    """Test refresh token endpoint"""
    print("\n🔄 Testing Refresh Token API...")
    
    if not refresh_token:
        print("❌ No refresh token provided")
        return None
    
    response = requests.post(
        f"{BASE_URL}/token/refresh/",
        json={"refresh": refresh_token},
        headers={"Content-Type": "application/json"}
    )
    
    print_response("Refresh Token Response", response)
    
    if response.status_code == 200:
        data = response.json()
        if "access" in data:
            print("✅ Refresh token successful - New access token received!")
            print(f"   New Access Token: {data['access'][:50]}...")
            return data
        else:
            print("❌ Refresh token successful but NO ACCESS TOKEN!")
            return None
    else:
        print("❌ Refresh token failed")
        return None


def test_me_endpoint(access_token):
    """Test /me endpoint with access token"""
    print("\n👤 Testing /me endpoint...")
    
    if not access_token:
        print("❌ No access token provided")
        return None
    
    response = requests.get(
        f"{BASE_URL}/me/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    
    print_response("Me Endpoint Response", response)
    
    if response.status_code == 200:
        print("✅ /me endpoint successful!")
        return response.json()
    else:
        print("❌ /me endpoint failed")
        return None


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 ACCOUNTS API TEST SUITE")
    print("="*60)
    
    # Test 1: sendMobile
    send_mobile_result = test_send_mobile()
    
    if send_mobile_result and not send_mobile_result.get("exists"):
        # Test 2: Register (if user doesn't exist)
        register_result = test_register()
        
        if register_result and "refresh" in register_result:
            # Test 3: Refresh Token
            test_refresh_token(register_result["refresh"])
            
            # Test 4: /me endpoint
            test_me_endpoint(register_result["access"])
    
    # Test 5: Login (always test login)
    login_result = test_login()
    
    if login_result and "refresh" in login_result:
        # Test 6: Refresh Token from login
        test_refresh_token(login_result["refresh"])
        
        # Test 7: /me endpoint with login token
        test_me_endpoint(login_result["access"])
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

