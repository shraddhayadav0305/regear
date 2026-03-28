#!/usr/bin/env python3
"""Test seller plans navigation"""
import sys
sys.path.insert(0, '.')

from app import app

print("=" * 70)
print("🧪 TESTING SELLER PLANS NAVIGATION")
print("=" * 70)

# Test 1: Check if routes exist
print("\n✓ Checking routes...")
routes_to_check = {
    '/seller-plans': 'seller_plans (NEW)',
    '/seller-packages': 'seller_packages (OLD - backup)',
}

with app.app_context():
    for route, desc in routes_to_check.items():
        found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == route:
                found = True
                print(f"  ✅ {route:25} → {desc}")
                break
        if not found:
            print(f"  ❌ {route:25} → NOT FOUND")

# Test 2: Check templates for navigation updates
print("\n✓ Checking template updates...")
import os

template_checks = {
    'templates/dashboard.html': [
        ("sidebar", "Sidebar menu"),
        ("seller_plans", "Updated route reference (sidebar)"),
        ("'/seller-packages'", "Backward compatibility check (sidebar)"),
    ],
    'templates/homepg.html': [
        ("Seller Plans", "Menu item text"),
        ("seller_plans", "Route in dropdown"),
        ('role == \'seller\'', "Role check for dropdown"),
    ],
}

for template_file, checks in template_checks.items():
    print(f"\n  📄 {template_file}:")
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for check_str, desc in checks:
                if check_str in content:
                    count = content.count(check_str)
                    print(f"    ✅ {desc:45} ({'found' if count == 1 else f'found {count}x'})")
                else:
                    print(f"    ❌ {desc:45} (NOT FOUND)")
    else:
        print(f"    ⚠️  File not found: {template_file}")

print("\n" + "=" * 70)
print("✅ SELLER PLANS NAVIGATION TEST COMPLETE")
print("=" * 70)
print("\n📋 EXPECTED USER EXPERIENCE:")
print("  ✓ Sellers see 'Seller Plans' in sidebar (left + active state)")
print("  ✓ Sellers see 'Seller Plans' in profile dropdown (top-right)")
print("  ✓ Menu highlights when on plans page")
print("  ✓ Both old (/seller-packages) and new (/seller-plans) route work")
print("\n🚀 NEXT STEPS:")
print("  1. Start Flask app: python app.py")
print("  2. Login as seller")
print("  3. Check sidebar - should see 'Seller Plans' option")
print("  4. Check profile dropdown - should see 'Seller Plans' option")
print("  5. Click 'Seller Plans' - should highlight in menu")
print("=" * 70)
