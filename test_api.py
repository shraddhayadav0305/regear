import requests
import json
import time

# Wait for server to start
time.sleep(2)

print("Testing /api/categories endpoint...")
try:
    response = requests.get('http://localhost:5000/api/categories')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nCategories returned: {len(data)}")
        
        # Check first category
        for i, (cat_name, cat_data) in enumerate(list(data.items())[:3]):
            print(f"\n{i+1}. {cat_name}")
            print(f"   Icon: {cat_data.get('icon', 'N/A')}")
            print(f"   Subcategories: {len(cat_data.get('subcategories', []))}")
            
            if cat_data.get('subcategories'):
                for sub in cat_data['subcategories'][:2]:
                    print(f"      - {sub['name']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")

print("\n\nTesting /subcategories route...")
try:
    response = requests.get('http://localhost:5000/subcategories?category=Mobile%20Phones')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Subcategories page loaded successfully")
        # Check if subcategories are in the HTML
        if 'subcategories' in response.text.lower():
            print("✅ Subcategories data found in response")
        else:
            print("❌ Subcategories data NOT found in response")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Connection error: {e}")
