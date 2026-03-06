from app import app

# Get all registered routes
routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': list(rule.methods - {'OPTIONS', 'HEAD'}),
        'path': str(rule)
    })

# Show admin routes
print('Admin Routes:')
print('=' * 80)
admin_routes = [r for r in routes if 'admin' in r['endpoint']]
if admin_routes:
    for route in admin_routes[:15]:
        print(f"{route['endpoint']:<40} {route['path']:<40}")
else:
    print('⚠️  NO ADMIN ROUTES FOUND!')
    
print('\n' + '=' * 80)
print(f"Total admin routes: {len(admin_routes)}")
