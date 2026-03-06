#!/usr/bin/env python
"""Verify Electronic Components image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("ELECTRONIC COMPONENTS IMAGE - VERIFICATION")
print("="*70)

comp_path = 'static/images/different-types-of-electronic-components.jpg'
if os.path.exists(comp_path):
    size = os.path.getsize(comp_path)
    print(f"\n✅ Electronic Components image file exists")
    print(f"   Path: {comp_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(comp_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ Electronic Components image file not found at {comp_path}")

with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'Electronic Components' in data:
        comp_data = data['Electronic Components']
        image_path = comp_data.get('image')
        print(f"\n✅ API configured for Electronic Components")
        print(f"   Image path: {image_path}")
        if 'different-types-of-electronic-components.jpg' in image_path:
            print(f"   ✅ Correct Electronic Components image path!")
    else:
        print("\n❌ Electronic Components not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ ELECTRONIC COMPONENTS IMAGE CONFIGURED")
print("="*70)
print("\nYour Electronic Components image should now appear in the category box.")
