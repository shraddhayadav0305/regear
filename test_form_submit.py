import requests

# Test the payment page form submission
try:
    session = requests.Session()

    # First, let's try to access the boost page to see if we get redirected to login
    response = session.get('http://localhost:5000/boost/1')  # Assuming listing ID 1 exists
    print(f'Boost page status: {response.status_code}')
    print(f'Boost page redirect: {response.headers.get("Location", "None")}')

    # Now try to POST to payment page with form data
    form_data = {
        'ad_id': '1',
        'plan': 'basic',
        'price': '19',
        'days': '3',
        'boost_priority': '1'
    }

    response = session.post('http://localhost:5000/payment', data=form_data)
    print(f'Payment POST status: {response.status_code}')
    print(f'Payment POST redirect: {response.headers.get("Location", "None")}')
    print(f'Content length: {len(response.text)}')

    if 'login' in response.text.lower():
        print('Response contains login page - user not authenticated')
    elif 'payment' in response.text.lower():
        print('Response contains payment content - form submission worked')
    else:
        print('Response content preview:', response.text[:300])

except Exception as e:
    print(f'Error: {e}')