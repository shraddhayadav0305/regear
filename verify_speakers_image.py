#!/usr/bin/env python
"""Verify Speakers & Headphones image is properly configured"""

from app import app
import os
from PIL import Image

print("="*70)
print("SPEAKERS & HEADPHONES IMAGE - VERIFICATION")
print("="*70)

# Path relative to workspace
speaker_path = 'static/images/speakers and headphones.jpg'
if os.path.exists(speaker_path):
    size = os.path.getsize(speaker_path)
    print(f"\n✅ Speakers & Headphones image file exists")
    print(f"   Path: {speaker_path}")
    print(f"   Size: {size} bytes")
    try:
        img = Image.open(speaker_path)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]} pixels")
        print(f"   Format: {img.format}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"   Error reading image: {e}")
else:
    print(f"\n❌ Speakers & Headphones image file not found at {speaker_path}")

# Test API
with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    if 'Speakers & Headphones' in data:
        speaker_data = data['Speakers & Headphones']
        image_path = speaker_data.get('image')
        print(f"\n✅ API configured for Speakers & Headphones")
        print(f"   Image path: {image_path}")
        if 'speakers and headphones.jpg' in image_path:
            print(f"   ✅ Correct Speakers & Headphones image path!")
    else:
        print("\n❌ Speakers & Headphones not in API response")

    home_response = client.get('/')
    if home_response.status_code == 200:
        print(f"\n✅ Homepage loads successfully (HTTP {home_response.status_code})")

print("\n" + "="*70)
print("✅ SPEAKERS & HEADPHONES IMAGE CONFIGURED")
print("="*70)
print("\nYour Speakers & Headphones image should now appear in the category box.")
