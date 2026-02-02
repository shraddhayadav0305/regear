#!/usr/bin/env python3
"""Quick manual test of admin login functionality"""

import requests
import time
import sys

BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_admin_login():
    """Test admin login and dashboard access"""
    print("\n✅ TEST 1: Admin User Login")
    print("-" * 50)
    
    # Admin login
    response = session.post(f"{BASE_URL}/login", data={
        "email": "admin@regear.com",
        "password": "admin123"
    })
    
    print(f"Login response: {response.status_code}")
    
    # Try to access admin dashboard
    response = session.get(f"{BASE_URL}/admin/dashboard")
    print(f"Admin dashboard access: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ PASS: Admin can access dashboard")
    else:
        print("❌ FAIL: Admin cannot access dashboard")
    
    session.cookies.clear()

def test_buyer_denied():
    """Test that buyer cannot access admin routes"""
    print("\n✅ TEST 2: Buyer User Access (Should be Denied)")
    print("-" * 50)
    
    # Buyer login
    response = session.post(f"{BASE_URL}/login", data={
        "email": "buyer@test.com",
        "password": "buyer123"
    })
    
    print(f"Login response: {response.status_code}")
    
    # Try to access admin dashboard
    response = session.get(f"{BASE_URL}/admin/dashboard")
    print(f"Admin dashboard access attempt: {response.status_code}")
    
    if response.status_code != 200:
        print("✅ PASS: Buyer access properly denied (redirected)")
    else:
        print("❌ FAIL: Buyer was able to access admin dashboard!")
    
    session.cookies.clear()

def test_blocked_user():
    """Test that blocked user cannot login"""
    print("\n✅ TEST 3: Blocked User Login (Should be Denied)")
    print("-" * 50)
    
    # Blocked user login attempt
    response = session.post(f"{BASE_URL}/login", data={
        "email": "blocked@test.com",
        "password": "blocked123"
    }, allow_redirects=False)
    
    print(f"Login response: {response.status_code}")
    print(f"Location header: {response.headers.get('Location', 'N/A')}")
    
    # Check if redirected (status 302) - should be denied
    if response.status_code == 302 or response.status_code == 200:
        # Check for redirect or flash message
        if 'blocked' in response.text.lower() or response.status_code == 302:
            print("✅ PASS: Blocked user properly rejected")
        else:
            print("❌ FAIL: Blocked user was able to login")
    
    session.cookies.clear()

def test_invalid_credentials():
    """Test that invalid credentials are rejected"""
    print("\n✅ TEST 4: Invalid Credentials")
    print("-" * 50)
    
    # Invalid user login
    response = session.post(f"{BASE_URL}/login", data={
        "email": "nonexistent@test.com",
        "password": "wrongpassword"
    })
    
    print(f"Login response: {response.status_code}")
    
    # Should not have access to admin
    response = session.get(f"{BASE_URL}/admin/dashboard")
    print(f"Admin dashboard access: {response.status_code}")
    
    if response.status_code != 200:
        print("✅ PASS: Invalid user access properly denied")
    else:
        print("❌ FAIL: Invalid user was granted access!")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("ReGear Admin Login Testing")
    print("="*50)
    
    # Wait for server
    print("\n⏳ Checking if Flask server is running...")
    for i in range(5):
        try:
            requests.get(f"{BASE_URL}/health")
            print("✅ Flask server is ready!\n")
            break
        except:
            if i < 4:
                print(f"   Attempt {i+1}/5: Waiting...")
                time.sleep(1)
            else:
                print("❌ Flask server not responding. Please start it with: python app.py")
                sys.exit(1)
    
    try:
        test_admin_login()
        test_buyer_denied()
        test_blocked_user()
        test_invalid_credentials()
        
        print("\n" + "="*50)
        print("✅ Testing Complete!")
        print("="*50 + "\n")
    except Exception as e:
        print(f"❌ Test error: {e}")
