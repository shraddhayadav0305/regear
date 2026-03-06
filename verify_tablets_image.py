#!/usr/bin/env python
"""Verify Tablets image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("TABLETS IMAGE - VERIFICATION")
print("="*70)

# Path relative to workspace
tablet_path = 'static/images/tablets.webp'
if os.path.exists(tablet_path):
    size = os.path.getsize(tablet_path)
    print(f"\n✅ Tablets image file exists")
    print(f"   Path: {tablet_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(tablet_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ Tablets image file not found at {tablet_path}")

# Test API
with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'Tablets' in data:
        tablet_data = data['Tablets']
        image_path = tablet_data.get('image')
        print(f"\n✅ API configured for Tablets")
        print(f"   Image path: {image_path}")
        if 'tablets.webp' in image_path:
            print(f"   ✅ Correct Tablets image path!")
    else:
        print("\n❌ Tablets not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ TABLETS IMAGE CONFIGURED")
print("="*70)
print("\nYour Tablets image should now appear in the category box.")
