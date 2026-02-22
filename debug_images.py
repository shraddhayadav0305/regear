#!/usr/bin/env python
"""Debug category image rendering"""

from app import app
import re

with app.test_client() as client:
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Extract the loadCategories function
    match = re.search(r'function loadCategories\(\).*?(?=\n    function|\n    // Initialize)', html, re.DOTALL)
    if match:
        func = match.group(0)
        print("Current loadCategories() function:")
        print("="*80)
        print(func[:500])
        print("\n... (truncated)")
        
        # Check what's in the HTML
        if 'background-image' in func:
            print("\n✓ Background image inline style is being applied")
        if 'catData.image' in func:
            print("✓ Using catData.image from API")
            
            # Extract a sample to see what the style looks like
            style_match = re.search(r'style="\$\{bgImage\}"', func)
            if style_match:
                print(f"✓ Style pattern: {style_match.group(0)}")
    
    # Check API response
    api_response = client.get('/api/categories')
    data = api_response.get_json()
    
    print("\n" + "="*80)
    print("Sample category from API:")
    print("="*80)
    
    sample = list(data.items())[0]
    print(f"Category: {sample[0]}")
    print(f"Image URL: {sample[1].get('image')}")
    
    # Try to fetch the image
    import urllib.request
    try:
        image_url = sample[1].get('image')
        if image_url:
            urllib.request.urlopen(image_url, timeout=5)
            print("✓ Image URL is accessible")
    except Exception as e:
        print(f"✗ Image URL not accessible: {e}")
