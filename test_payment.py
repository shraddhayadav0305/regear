import requests

# Test the payment page route
try:
    # First, let's see if we can access the home page
    response = requests.get('http://localhost:5000/')
    print(f'Home page status: {response.status_code}')

    # Try to access payment page directly (will likely redirect due to login_required)
    response = requests.get('http://localhost:5000/payment')
    print(f'Payment page status: {response.status_code}')
    print(f'Redirect location: {response.headers.get("Location", "None")}')

except Exception as e:
    print(f'Error: {e}')