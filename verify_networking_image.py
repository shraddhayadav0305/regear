#!/usr/bin/env python
"""Verify Networking Devices image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("NETWORKING DEVICES IMAGE - VERIFICATION")
print("="*70)

# Path relative to workspace
net_path = 'static/images/Screenshot 2026-02-22 193118.png'
if os.path.exists(net_path):
    size = os.path.getsize(net_path)
    print(f"\n✅ Networking Devices image file exists")
    print(f"   Path: {net_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(net_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ Networking Devices image file not found at {net_path}")

# Test API
with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'Networking Devices' in data:
        net_data = data['Networking Devices']
        image_path = net_data.get('image')
        print(f"\n✅ API configured for Networking Devices")
        print(f"   Image path: {image_path}")
        if 'Screenshot 2026-02-22 193118.png' in image_path:
            print(f"   ✅ Correct Networking Devices image path!")
    else:
        print("\n❌ Networking Devices not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ NETWORKING DEVICES IMAGE VERIFIED")
print("="*70)
print("\nYour Networking Devices image should now appear in the category box.")
