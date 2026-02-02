#!/usr/bin/env python3
"""Test admin products page by logging in and requesting /admin/products"""
import requests
from urllib.parse import urljoin

BASE = "http://localhost:5000"
ADMIN_EMAIL = "admin@regear.com"
ADMIN_PASSWORD = "admin123"

s = requests.Session()

print("Logging in as admin...")
resp = s.get(urljoin(BASE, "/login"))
if resp.status_code != 200:
    print("WARNING: /login GET returned", resp.status_code)

login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
resp = s.post(urljoin(BASE, "/login"), data=login_data, allow_redirects=True)
print("Login POST ->", resp.status_code)

# Now request admin products
resp = s.get(urljoin(BASE, "/admin/products"))
print("GET /admin/products ->", resp.status_code)

content = resp.text or ''
if resp.status_code == 200:
    snippet = content[:1000]
    print("Page contains (first 1000 chars):\n", snippet)
    if 'Product Management' in content or 'Products (' in content:
        print("SUCCESS: Admin products page loaded")
    else:
        print("NOTICE: Page loaded but expected markers not found")
else:
    print("Error response body (first 1000 chars):\n", content[:1000])
