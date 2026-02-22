#!/usr/bin/env python
"""Test that category images are now being returned from the API"""

from app import app
import json

with app.test_client() as client:
    response = client.get('/api/categories')
    data = response.get_json()
    
    print("=" * 60)
    print("CATEGORY IMAGE UPDATE TEST")
    print("=" * 60)
    
    print(f"\nTotal categories: {len(data)}")
    
    # Check first 5 categories
    print("\nFirst 5 Categories:")
    for i, (cat, cat_data) in enumerate(list(data.items())[:5]):
        has_image = bool(cat_data.get('image'))
        print(f"  {i+1}. {cat}: {'✓ Image URL' if has_image else '✗ No image'}")
    
    # Check if "View All" is in the data
    has_view_all = 'View All' in data
    print(f"\n'View All' present in API: {'❌ YES (should be removed)' if has_view_all else '✓ NO (removed as requested)'}")
    
    # Verify all categories have images
    all_have_images = all(v.get('image') for v in data.values())
    print(f"All categories have images: {'✓ YES' if all_have_images else '❌ NO'}")
    
    # Show sample image URL
    first_cat = list(data.items())[0]
    print(f"\nSample image URL: {first_cat[1].get('image', 'N/A')}")
    
    print("\n" + "=" * 60)
    if all_have_images and not has_view_all:
        print("✅ CATEGORY IMAGE UPDATE SUCCESSFUL")
    else:
        print("⚠️ ISSUES DETECTED - See above")
    print("=" * 60)
