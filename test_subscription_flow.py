#!/usr/bin/env python3
"""Test subscription payment flow"""
import sys
sys.path.insert(0, '.')

from app import app
import json

print("=" * 60)
print("🧪 TESTING SUBSCRIPTION FLOW")
print("=" * 60)

# Test 1: Check if routes exist
print("\n✓ Checking routes...")
routes_to_check = [
    '/seller-packages',
    '/subscription-payment', 
    '/process-subscription-payment',
    '/subscription-success',
    '/subscription-transactions'
]

with app.app_context():
    for route in routes_to_check:
        found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == route:
                found = True
                print(f"  ✅ {route} → {rule.endpoint} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
                break
        if not found:
            print(f"  ❌ {route} NOT FOUND")

# Test 2: Check templates exist
print("\n✓ Checking templates...")
import os

templates_to_check = [
    'seller_packages.html',
    'subscription_payment.html',
    'subscription_success.html',
    'subscription_transactions.html'
]

for template in templates_to_check:
    path = f'templates/{template}'
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✅ {template} ({size} bytes)")
    else:
        print(f"  ❌ {template} NOT FOUND")

# Test 3: Verify form structure
print("\n✓ Checking form structure in seller_packages.html...")
with open('templates/seller_packages.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    required_fields = ['plan_name', 'price', 'ad_limit', 'duration_days']
    for field in required_fields:
        if f'name="{field}"' in content:
            count = content.count(f'name="{field}"')
            print(f"  ✅ {field} found {count}x in forms")
        else:
            print(f"  ❌ {field} NOT FOUND in forms")
    
    if 'action="/subscription-payment"' in content:
        count = content.count('action="/subscription-payment"')
        print(f"  ✅ Forms post to /subscription-payment ({count} forms)")
    else:
        print(f"  ❌ No forms posting to /subscription-payment")

# Test 4: Verify payment template structure
print("\n✓ Checking payment template structure...")
with open('templates/subscription_payment.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    checks = [
        ('<!DOCTYPE html>', 'HTML document structure'),
        ('<head>', 'Head section'),
        ('<body>', 'Body section'),
        ('action="/process-subscription-payment"', 'Payment form submission'),
        ('name="payment_method"', 'Payment method radio buttons'),
        ('id="payBtn"', 'Payment button'),
    ]
    for check, desc in checks:
        if check in content:
            print(f"  ✅ {desc}")
        else:
            print(f"  ❌ {desc} NOT FOUND")

print("\n" + "=" * 60)
print("✅ SUBSCRIPTION FLOW TEST COMPLETE")
print("=" * 60)
print("\n📋 NEXT STEPS:")
print("  1. Login to the app")
print("  2. Go to /seller-packages")
print("  3. Click 'Select Plan' on any plan")
print("  4. Verify redirect to payment page")
print("  5. Select payment method and click 'Pay'")
print("  6. Verify success page with transaction details")
print("=" * 60)
