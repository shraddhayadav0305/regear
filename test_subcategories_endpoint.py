import requests
from urllib.parse import quote

# Test the subcategories endpoint
test_categories = [
    "Mobile Phones",
    "Laptops & Computers",
    "Tablets",
    "Computer Accessories"
]

for cat in test_categories:
    # Encode the category name
    encoded = quote(cat)
    url = f"http://localhost:5000/subcategories?category={encoded}"
    print(f"\nTesting category: '{cat}'")
    print(f"URL: {url}")
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ SUCCESS - Got subcategories page")
        else:
            print(f"❌ FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
