#!/usr/bin/env python3
"""Test admin login and dashboard connection"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:5000"

def test_admin_login_flow():
    """Test the complete admin login flow"""
    session = requests.Session()
    
    print("=" * 60)
    print("Testing Admin Login Flow")
    print("=" * 60)
    
    # Admin credentials from database
    admin_email = "admin@regear.com"
    admin_password = "admin123"  # Default password used in setup
    
    # Step 1: Access login page
    print("\n1️⃣ Accessing login page...")
    response = session.get(f"{BASE_URL}/login")
    print(f"   Status: {response.status_code}")
    
    # Step 2: Submit login form
    print("\n2️⃣ Submitting login form...")
    login_data = {
        "email": admin_email,
        "password": admin_password
    }
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    print(f"   Redirect location: {response.headers.get('Location', 'None')}")
    
    # Step 3: Follow redirect
    if response.status_code in [301, 302, 303, 307, 308]:
        redirect_url = response.headers.get('Location')
        if redirect_url:
            full_redirect_url = urljoin(BASE_URL, redirect_url)
            print(f"\n3️⃣ Following redirect to: {full_redirect_url}")
            response = session.get(full_redirect_url, allow_redirects=True)
            print(f"   Status: {response.status_code}")
            
            # Check if we're on admin dashboard
            if "/admin/dashboard" in response.url or "Dashboard Overview" in response.text:
                print("\n   ✅ Successfully redirected to admin dashboard!")
                return True
            else:
                print(f"\n   ⚠️ Unexpected redirect to: {response.url}")
                return False
    
    return False

if __name__ == "__main__":
    success = test_admin_login_flow()
    print("\n" + "=" * 60)
    if success:
        print("✅ Admin login connection SUCCESSFUL!")
    else:
        print("❌ Admin login connection FAILED!")
    print("=" * 60)
