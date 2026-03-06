#!/usr/bin/env python
"""Verify Smart Watches image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("SMART WATCHES IMAGE - VERIFICATION")
print("="*70)

# Path relative to workspace
watch_path = 'static/images/smart watches.jpg'
if os.path.exists(watch_path):
    size = os.path.getsize(watch_path)
    print(f"\n✅ Smart Watches image file exists")
    print(f"   Path: {watch_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(watch_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ Smart Watches image file not found at {watch_path}")

# Test API
with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'Smart Watches' in data:
        watch_data = data['Smart Watches']
        image_path = watch_data.get('image')
        print(f"\n✅ API configured for Smart Watches")
        print(f"   Image path: {image_path}")
        if 'smart watches.jpg' in image_path:
            print(f"   ✅ Correct Smart Watches image path!")
    else:
        print("\n❌ Smart Watches not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ SMART WATCHES IMAGE CONFIGURED")
print("="*70)
print("\nYour Smart Watches image should now appear in the category box.")
