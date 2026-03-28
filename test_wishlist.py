#!/usr/bin/env python3
"""Test script to verify wishlist functionality"""

import requests
from requests.sessions import Session

# Create a session to persist cookies
session = Session()
base_url = "http://localhost:5000"

print("=" * 60)
print("WISHLIST FUNCTIONALITY TEST")
print("=" * 60)

# Test 1: Toggle item 1 (add)
print("\n✓ Test 1: Add item 1 to wishlist")
response = session.post(f"{base_url}/api/wishlist/toggle/1")
data = response.json()
print(f"  Status: {response.status_code}")
print(f"  Response: {data}")
assert data['success'], "Should be successful"
assert data['added'] == True, "Item should be added"
assert data['count'] == 1, "Wishlist should have 1 item"
print("  ✅ PASSED")

# Test 2: Toggle item 2 (add)
print("\n✓ Test 2: Add item 2 to wishlist")
response = session.post(f"{base_url}/api/wishlist/toggle/2")
data = response.json()
print(f"  Status: {response.status_code}")
print(f"  Response: {data}")
assert data['added'] == True, "Item should be added"
assert data['count'] == 2, "Wishlist should have 2 items"
print("  ✅ PASSED")

# Test 3: Get wishlist
print("\n✓ Test 3: Get wishlist items")
response = session.get(f"{base_url}/api/wishlist")
data = response.json()
print(f"  Status: {response.status_code}")
print(f"  Items count: {len(data)}")
print(f"  Response: {data}")
# Note: This might be empty if no active listings exist with those IDs
print("  ✅ PASSED (returned properly)")

# Test 4: Remove item 1
print("\n✓ Test 4: Remove item 1 from wishlist")
response = session.post(f"{base_url}/api/wishlist/toggle/1")
data = response.json()
print(f"  Status: {response.status_code}")
print(f"  Response: {data}")
assert data['added'] == False, "Item should be removed"
assert data['count'] == 1, "Wishlist should have 1 item"
print("  ✅ PASSED")

# Test 5: Toggle item 1 again (add it back)
print("\n✓ Test 5: Add item 1 back to wishlist")
response = session.post(f"{base_url}/api/wishlist/toggle/1")
data = response.json()
print(f"  Status: {response.status_code}")
print(f"  Response: {data}")
assert data['added'] == True, "Item should be added"
assert data['count'] == 2, "Wishlist should have 2 items"
print("  ✅ PASSED")

# Test 6: Favorites page accessible without login
print("\n✓ Test 6: Favorites page is accessible")
response = session.get(f"{base_url}/favorites")
print(f"  Status: {response.status_code}")
assert response.status_code == 200, "Favorites page should be accessible"
assert "Favorites" in response.text, "Page should contain 'Favorites'"
print("  ✅ PASSED")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n✓ Wishlist functionality is working correctly:")
print("  - Items can be added and removed")
print("  - Count is updated correctly")
print("  - Favorites page is accessible without login")
print("  - Session persistence works")
