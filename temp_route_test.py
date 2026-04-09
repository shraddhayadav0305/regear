from app import app

with app.test_client() as client:
    for slug in ['mobile_phones', 'mobile-phones', 'laptops_computers', 'laptops-computers', 'cameras_dslr', 'cameras-dslr']:
        resp = client.get(f'/category/{slug}')
        print(slug, resp.status_code, 'OK' if resp.status_code==200 else resp.location or resp.data[:100])
