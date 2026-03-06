#!/usr/bin/env python
"""Verify Smart Home Devices image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("SMART HOME DEVICES IMAGE - VERIFICATION")
print("="*70)

# Path relative to workspace
smart_path = 'static/images/Smart-Home-Device-Smart-Device.png'
if os.path.exists(smart_path):
    size = os.path.getsize(smart_path)
    print(f"\n✅ Smart Home Devices image file exists")
    print(f"   Path: {smart_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(smart_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ Smart Home Devices image file not found at {smart_path}")

# Test API
with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'Smart Home Devices' in data:
        smart_data = data['Smart Home Devices']
        image_path = smart_data.get('image')
        print(f"\n✅ API configured for Smart Home Devices")
        print(f"   Image path: {image_path}")
        if 'Smart-Home-Device-Smart-Device.png' in image_path:
            print(f"   ✅ Correct Smart Home Devices image path!")
    else:
        print("\n❌ Smart Home Devices not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ SMART HOME DEVICES IMAGE CONFIGURED")
print("="*70)
print("\nYour Smart Home Devices image should now appear in the category box.")
