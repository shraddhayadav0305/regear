#!/usr/bin/env python3
"""
Test script to verify all categories can be accessed via the subcategories endpoint
"""
import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:5000"

# First, get all categories
print("=" * 80)
print("FETCHING ALL CATEGORIES FROM API")
print("=" * 80)

try:
    with urllib.request.urlopen(f"{BASE_URL}/api/categories") as response:
        api_data = json.loads(response.read().decode())
        
    categories = list(api_data.keys())
    print(f"\n✅ Found {len(categories)} categories:")
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat}")
    
    print("\n" + "=" * 80)
    print("TESTING SUBCATEGORIES ENDPOINT FOR EACH CATEGORY")
    print("=" * 80)
    
    results = {}
    for cat in categories:
        encoded_cat = urllib.parse.quote(cat)
        url = f"{BASE_URL}/subcategories?category={encoded_cat}"
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read().decode()
                # Check if the category name appears in the response
                if cat in html:
                    results[cat] = "✅ WORKS"
                else:
                    results[cat] = "⚠️  Page loaded but category not in response"
        except urllib.error.HTTPError as e:
            if e.code == 302:  # Redirect (probably due to invalid category)
                results[cat] = "❌ REDIRECTED (Invalid category)"
            else:
                results[cat] = f"❌ HTTP ERROR {e.code}"
        except Exception as e:
            results[cat] = f"❌ ERROR: {str(e)}"
    
    print("\nRESULTS:")
    print("-" * 80)
    working = sum(1 for r in results.values() if "✅" in r)
    total = len(results)
    
    for cat, result in results.items():
        print(f"  {result}  {cat}")
    
    print("-" * 80)
    print(f"\nSUMMARY: {working}/{total} categories working")
    
    if working == total:
        print("✅ ALL CATEGORIES WORKING!")
    else:
        print(f"❌ {total - working} categories not working")
        
except Exception as e:
    print(f"❌ Error: {e}")
