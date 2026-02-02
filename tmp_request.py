import requests
from urllib.parse import urljoin
BASE='http://localhost:5000'
admin_email='admin@regear.com'
admin_pass='admin123'
s=requests.Session()
print('GET /login =>', s.get(urljoin(BASE,'/login')).status_code)
resp=s.post(urljoin(BASE,'/login'), data={'email':admin_email,'password':admin_pass}, allow_redirects=True)
print('POST /login =>', resp.status_code)
resp=s.get(urljoin(BASE,'/admin/products'))
print('/admin/products =>', resp.status_code)
print(resp.text[:800])
