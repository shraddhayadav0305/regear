#!/usr/bin/env python3
"""
Minimal test to check ad posting debug output
"""

import requests

def test_minimal():
    """Minimal test to see debug output"""
    print("Testing minimal ad post...")

    # Create a session and login first
    session = requests.Session()

    # Try to login with existing seller user
    login_data = {'email': 'seller@test.com', 'password': 'seller123'}  # Assuming this exists
    response = session.post("http://localhost:5000/login", data=login_data, allow_redirects=False)
    print(f"Login: {response.status_code} -> {response.headers.get('Location', 'None')}")
    print(f"Session cookies after login: {session.cookies.get_dict()}")

    # Check if we're logged in by accessing dashboard
    response = session.get("http://localhost:5000/dashboard", allow_redirects=False)
    print(f"Dashboard access: {response.status_code}")

    # Try GET request to post-ad first
    response = session.get("http://localhost:5000/post-ad", allow_redirects=False)
    print(f"GET post-ad: {response.status_code} -> {response.headers.get('Location', 'None')}")

    # Try to post ad
    ad_data = {
        'title': 'Debug Test Ad',
        'description': 'Testing debug output',
        'price': '100',
        'category': 'Mobiles',
        'subcategory': 'iPhone',
        'condition': 'new',
        'location': 'Delhi',
        'phone': '1234567890',
        'email': 'seller@test.com'
    }

    response = session.post("http://localhost:5000/post-ad", data=ad_data, allow_redirects=False)
    print(f"Post ad: {response.status_code} -> {response.headers.get('Location', 'None')}")
    print(f"Session cookies after post: {session.cookies.get_dict()}")

if __name__ == "__main__":
    test_minimal()