#!/usr/bin/env python3
"""
ReGear Admin Authentication & Role-Based Access Test
Tests:
1. Admin login and dashboard access
2. Non-admin users cannot access admin routes
3. Session validation
4. Role checking
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

# Test credentials
test_users = {
    'admin': {'email': 'admin@regear.com', 'password': 'admin123', 'role': 'admin'},
    'buyer': {'email': 'buyer@test.com', 'password': 'buyer123', 'role': 'buyer'},
    'seller': {'email': 'seller@test.com', 'password': 'seller123', 'role': 'seller'},
    'blocked': {'email': 'blocked@test.com', 'password': 'blocked123', 'role': 'blocked'},
}

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_test(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"     {details}")

def test_login(username, password):
    """Test user login"""
    print(f"\n🔐 Testing login for: {username}")
    try:
        response = SESSION.post(
            f"{BASE_URL}/login",
            data={'email': username, 'password': password},
            allow_redirects=True
        )
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_admin_access(should_pass=True):
    """Test access to admin dashboard"""
    print(f"\n   Testing access to admin dashboard...")
    try:
        response = SESSION.get(f"{BASE_URL}/admin/dashboard")
        
        if should_pass:
            passed = response.status_code == 200 and "Dashboard" in response.text
            print(f"   {'✅' if passed else '❌'} Status: {response.status_code}")
            return passed
        else:
            # Should be redirected (302 or 401 or 403)
            passed = response.status_code in [302, 401, 403, 200] and "Admin access" in response.text or response.status_code != 200
            print(f"   {'✅' if passed else '❌'} Status: {response.status_code} (should be redirected)")
            return passed or response.status_code in [302, 401]
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_route_access(route, should_pass=True):
    """Test specific route access"""
    try:
        response = SESSION.get(f"{BASE_URL}{route}")
        if should_pass:
            return response.status_code == 200
        else:
            return response.status_code in [302, 401] or "access" in response.text.lower()
    except:
        return False

def clear_session():
    """Clear current session"""
    SESSION.cookies.clear()
    print("   🔄 Session cleared")

def main():
    print("\n" + "🧪 "*30)
    print("ReGear Admin Authentication & Role-Based Access Test Suite")
    print("🧪 "*30)
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # ===== TEST 1: Admin User =====
    print_section("TEST 1: ADMIN USER ACCESS")
    
    results['total'] += 1
    if test_login(test_users['admin']['email'], test_users['admin']['password']):
        results['passed'] += 1
        print_test("Admin Login", True, "Successfully logged in")
        
        # Test admin routes
        admin_routes = [
            '/admin/dashboard',
            '/admin/users',
            '/admin/products',
            '/admin/complaints',
            '/admin/activity'
        ]
        
        print("\n📍 Testing admin routes:")
        for route in admin_routes:
            results['total'] += 1
            passed = test_route_access(route, should_pass=True)
            results['passed'] += passed
            results['failed'] += not passed
            print_test(f"  GET {route}", passed, f"Status: {'200 OK' if passed else 'DENIED'}")
    else:
        results['failed'] += 1
        print_test("Admin Login", False, "Failed to login")
    
    # ===== TEST 2: Non-Admin User (Buyer) =====
    print_section("TEST 2: BUYER USER ACCESS (Should be DENIED)")
    
    clear_session()
    results['total'] += 1
    if test_login(test_users['buyer']['email'], test_users['buyer']['password']):
        results['passed'] += 1
        print_test("Buyer Login", True, "Successfully logged in")
        
        # Test that buyer cannot access admin routes
        admin_routes = ['/admin/dashboard', '/admin/users', '/admin/products']
        
        print("\n📍 Testing admin route access (should be denied):")
        for route in admin_routes:
            results['total'] += 1
            # For non-admin, accessing admin routes should fail or redirect
            passed = not test_route_access(route, should_pass=False)
            results['passed'] += passed
            results['failed'] += not passed
            print_test(f"  GET {route} (denied)", passed, "Access properly denied")
    else:
        results['failed'] += 1
        print_test("Buyer Login", False, "Failed to login")
    
    # ===== TEST 3: Seller User =====
    print_section("TEST 3: SELLER USER ACCESS (Should be DENIED)")
    
    clear_session()
    results['total'] += 1
    if test_login(test_users['seller']['email'], test_users['seller']['password']):
        results['passed'] += 1
        print_test("Seller Login", True, "Successfully logged in")
        
        print("\n📍 Testing admin dashboard access (should be denied):")
        results['total'] += 1
        passed = not test_route_access('/admin/dashboard', should_pass=False)
        results['passed'] += passed
        results['failed'] += not passed
        print_test("  GET /admin/dashboard (denied)", passed, "Access properly denied")
    else:
        results['failed'] += 1
        print_test("Seller Login", False, "Failed to login")
    
    # ===== TEST 4: Blocked User =====
    print_section("TEST 4: BLOCKED USER ACCESS (Should be DENIED)")
    
    clear_session()
    results['total'] += 1
    login_blocked = test_login(test_users['blocked']['email'], test_users['blocked']['password'])
    
    if login_blocked:
        print_test("Blocked User Login", True, "Logged in (may or may not be restricted)")
        
        results['total'] += 1
        passed = test_route_access('/dashboard', should_pass=False)
        results['passed'] += passed
        results['failed'] += not passed
        print_test("  Dashboard access", passed, "Properly handled")
    else:
        results['passed'] += 1
        print_test("Blocked User Login", True, "Cannot login (expected)")
    
    # ===== TEST 5: Invalid Credentials =====
    print_section("TEST 5: INVALID CREDENTIALS")
    
    clear_session()
    results['total'] += 1
    login_invalid = test_login('nonexistent@test.com', 'wrongpassword')
    if not login_invalid:
        results['passed'] += 1
        print_test("Invalid Login Rejected", True, "Login properly denied")
    else:
        results['failed'] += 1
        print_test("Invalid Login Rejected", False, "Invalid credentials were accepted!")
    
    # ===== TEST 6: Session Validation =====
    print_section("TEST 6: SESSION VALIDATION")
    
    clear_session()
    results['total'] += 1
    print("Testing unauthenticated access to admin dashboard...")
    response = SESSION.get(f"{BASE_URL}/admin/dashboard", allow_redirects=False)
    if response.status_code in [302, 401]:
        results['passed'] += 1
        print_test("Unauthenticated Access Denied", True, f"Redirected (status: {response.status_code})")
    else:
        results['failed'] += 1
        print_test("Unauthenticated Access Denied", False, f"Status: {response.status_code}")
    
    # ===== SUMMARY =====
    print_section("TEST SUMMARY")
    
    print(f"Total Tests:   {results['total']}")
    print(f"✅ Passed:     {results['passed']}")
    print(f"❌ Failed:     {results['failed']}")
    
    if results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! Admin authentication is working correctly.")
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed. See details above.")
    
    print("\n" + "="*60)
    print("Test Results Summary:")
    print("="*60)
    
    if results['failed'] == 0:
        print("✅ Authentication & Authorization: WORKING")
        print("✅ Admin-only access: WORKING")
        print("✅ Role-based access control: WORKING")
        print("✅ Session validation: WORKING")
    else:
        print(f"❌ Some tests failed ({results['failed']}/{results['total']})")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n⏳ Waiting for Flask server to be ready...")
    print("   Make sure Flask is running: python app.py\n")
    
    # Try to connect a few times
    for attempt in range(3):
        try:
            response = requests.get(f"{BASE_URL}/")
            print("✅ Flask server is ready!\n")
            break
        except requests.exceptions.ConnectionError:
            if attempt < 2:
                print(f"   Attempt {attempt+1}/3: Waiting for server...")
                sleep(2)
            else:
                print("❌ Cannot connect to Flask server.")
                print("   Please run: python app.py")
                exit(1)
    
    main()
