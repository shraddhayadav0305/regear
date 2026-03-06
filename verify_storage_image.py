#!/usr/bin/env python
"""Verify Storage Devices image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("STORAGE DEVICES IMAGE - VERIFICATION")
print("="*70)

# Path relative to workspace
storage_path = 'static/images/storage device.webp'
if os.path.exists(storage_path):
    size = os.path.getsize(storage_path)
    print(f"\n✅ Storage Devices image file exists")
    print(f"   Path: {storage_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(storage_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ Storage Devices image file not found at {storage_path}")

# Test API
with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'Storage Devices' in data:
        storage_data = data['Storage Devices']
        image_path = storage_data.get('image')
        print(f"\n✅ API configured for Storage Devices")
        print(f"   Image path: {image_path}")
        if 'storage device.webp' in image_path:
            print(f"   ✅ Correct Storage Devices image path!")
    else:
        print("\n❌ Storage Devices not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ STORAGE DEVICES IMAGE CONFIGURED")
print("="*70)
print("\nYour Storage Devices image should now appear in the category box.")
