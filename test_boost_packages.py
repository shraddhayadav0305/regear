# Test the boost packages page
import requests

session = requests.Session()

# Try to access boost packages page
response = session.get('http://localhost:5000/boost/29')  # Use existing listing ID
print(f'Boost packages page status: {response.status_code}')

if response.status_code == 200:
    if 'boost_packages' in response.text:
        print('✓ boost_packages.html is being rendered')
    else:
        print('✗ boost_packages.html not found in response')

    if 'SELECT PLAN' in response.text:
        print('✓ SELECT PLAN buttons found')
    else:
        print('✗ SELECT PLAN buttons not found')

    if 'payment_page' in response.text:
        print('✓ url_for payment_page found in template')
    else:
        print('✗ url_for payment_page not found in template')

    # Check if form action is correct
    if 'action="/payment"' in response.text:
        print('✓ Form action points to /payment')
    else:
        print('✗ Form action not found or incorrect')
else:
    print(f'✗ Could not access boost packages page: {response.status_code}')