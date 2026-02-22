#!/usr/bin/env python
"""Test that homepage displays category images correctly"""

from app import app
import re

with app.test_client() as client:
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    print("=" * 60)
    print("HOMEPAGE CATEGORY DISPLAY TEST")
    print("=" * 60)
    
    # Check for the updated JavaScript function
    has_bg_image = 'background-image: url' in html
    has_category_icon_box = 'category-icon-box' in html
    
    # Check CSS updates
    has_100px = 'width: 100px' in html and 'height: 100px' in html
    has_background_size = 'background-size: cover' in html
    has_no_view_all = 'View All' not in html or 'View All' not in re.findall(r'loadCategories.*?=.*?}', html, re.DOTALL)[0] if re.findall(r'loadCategories.*?=.*?}', html, re.DOTALL) else True
    
    print("\n✓ Homepage loads successfully" if response.status_code == 200 else "✗ Homepage failed to load")
    print(f"{'✓' if has_bg_image else '✗'} JavaScript uses background-image for category display")
    print(f"{'✓' if has_100px else '✗'} CSS updated to 100px category boxes")
    print(f"{'✓' if has_background_size else '✗'} CSS includes background-size: cover for images")
    print(f"{'✓' if has_category_icon_box else '✗'} category-icon-box class properly defined")
    
    # Check for the loadCategories function with new code
    load_categories_match = re.search(r'function loadCategories\(\).*?^    \}', html, re.MULTILINE | re.DOTALL)
    if load_categories_match:
        func_text = load_categories_match.group(0)
        has_new_logic = 'bgImage' in func_text and 'style="${bgImage}"' in func_text
        print(f"{'✓' if has_new_logic else '✗'} loadCategories() updated to use image backgrounds")
    else:
        print("✗ Could not find loadCategories function")
    
    print("\n" + "=" * 60)
    all_good = (response.status_code == 200 and has_bg_image and has_100px and 
                has_background_size and has_category_icon_box)
    if all_good:
        print("✅ HOMEPAGE CATEGORY DISPLAY READY")
    else:
        print("⚠️ SOME ISSUES DETECTED - See above")
    print("=" * 60)
