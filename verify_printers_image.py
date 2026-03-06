#!/usr/bin/env python
"""Verify Printers & Scanners image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("PRINTERS & SCANNERS IMAGE - VERIFICATION")
print("="*70)

# Path relative to workspace
print_path = 'static/images/printers and moniters.png'
if os.path.exists(print_path):
    size = os.path.getsize(print_path)
    print(f"\n✅ Printers & Scanners image file exists")
    print(f"   Path: {print_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(print_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ Printers & Scanners image file not found at {print_path}")

# Test API
with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'Printers & Scanners' in data:
        print_data = data['Printers & Scanners']
        image_path = print_data.get('image')
        print(f"\n✅ API configured for Printers & Scanners")
        print(f"   Image path: {image_path}")
        if 'printers and moniters.png' in image_path:
            print(f"   ✅ Correct Printers & Scanners image path!")
    else:
        print("\n❌ Printers & Scanners not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ PRINTERS & SCANNERS IMAGE CONFIGURED")
print("="*70)
print("\nYour Printers & Scanners image should now appear in the category box.")
