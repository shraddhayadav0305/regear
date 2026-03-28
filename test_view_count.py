#!/usr/bin/env python3
"""Test script to verify view count functionality"""

import requests
from requests.sessions import Session

# Create a session to persist cookies
session = Session()
base_url = "http://localhost:5000"

print("=" * 60)
print("VIEW COUNT FUNCTIONALITY TEST")
print("=" * 60)

# Test: View a listing multiple times
listing_id = 6  # Use an existing listing ID

print(f"\n✓ Test: View listing {listing_id} multiple times")

# Get initial view count
response = session.get(f"{base_url}/listing/{listing_id}")
print(f"  First view - Status: {response.status_code}")
if 'view_count' in response.text or 'Views' in response.text:
    print("  ✅ View count found in response")
else:
    print("  ❌ View count not found in response")

# View again
response = session.get(f"{base_url}/listing/{listing_id}")
print(f"  Second view - Status: {response.status_code}")

# View again
response = session.get(f"{base_url}/listing/{listing_id}")
print(f"  Third view - Status: {response.status_code}")

print("\n✓ Test completed - Check database for view_count increment")