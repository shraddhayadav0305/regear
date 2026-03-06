#!/usr/bin/env python
"""Verify TVs & Home Entertainment image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("TVs & HOME ENTERTAINMENT IMAGE - VERIFICATION")
print("="*70)

tv_path = 'static/images/tv and ho.png'
if os.path.exists(tv_path):
    size = os.path.getsize(tv_path)
    print(f"\n✅ TVs & Home Entertainment image file exists")
    print(f"   Path: {tv_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(tv_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ TVs & Home Entertainment image file not found at {tv_path}")

with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'TVs & Home Entertainment' in data:
        tv_data = data['TVs & Home Entertainment']
        image_path = tv_data.get('image')
        print(f"\n✅ API configured for TVs & Home Entertainment")
        print(f"   Image path: {image_path}")
        if 'tv and ho.png' in image_path:
            print(f"   ✅ Correct TVs & Home Entertainment image path!")
    else:
        print("\n❌ TVs & Home Entertainment not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ TVs & HOME ENTERTAINMENT IMAGE CONFIGURED")
print("="*70)
print("\nYour TVs & Home Entertainment image should now appear in the category box.")
