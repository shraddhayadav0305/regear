# Test the payment page route directly with a POST request
import requests

# Create a session and try to POST to payment page
session = requests.Session()

# Try to POST form data to payment page
form_data = {
    'ad_id': '29',  # Use an existing listing ID
    'plan': 'basic',
    'price': '19',
    'days': '3',
    'boost_priority': '1'
}

response = session.post('http://localhost:5000/payment', data=form_data, allow_redirects=False)
print(f'Payment POST status: {response.status_code}')
print(f'Payment POST redirect: {response.headers.get("Location", "None")}')

if response.status_code == 302:
    print('✓ Redirected (likely to login due to @login_required)')
elif response.status_code == 200:
    if 'payment' in response.text.lower():
        print('✓ Payment page rendered successfully')
    else:
        print('✗ Payment page not rendered')
else:
    print(f'✗ Unexpected status code: {response.status_code}')