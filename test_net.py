from app import app
with app.test_client() as c:
    response=c.get('/api/categories')
    data=response.get_json()
    net_data = data.get('Networking Devices', {})
    print("Networking Devices category:")
    print(f"  Image: {net_data.get('image')}")
    print(f"  Subcats: {len(net_data.get('subcategories', []))}")
