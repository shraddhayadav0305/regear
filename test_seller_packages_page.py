import requests
import sys

try:
    # Test the seller-packages page
    response = requests.get('http://localhost:5000/seller-packages', allow_redirects=False)
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Content Length: {len(response.text)}")
    print(f"✓ Has HTML: {'<html' in response.text.lower()}")
    print(f"✓ Has Starter plan: {'starter' in response.text.lower()}")
    print(f"✓ Has Growth plan: {'growth' in response.text.lower()}")
    print(f"✓ Has subscription-payment form: {'/subscription-payment' in response.text}")
    
    # Show first 500 chars
    print(f"\nFirst 500 characters:")
    print(response.text[:500])
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
