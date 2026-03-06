#!/usr/bin/env python
"""Test that my_listings.html renders correctly with new template structure."""

import sys
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from flask import Flask, url_for

# Setup Flask app for url_for context
app = Flask(__name__)
app.config['TESTING'] = True

# Create some dummy routes so url_for works
@app.route('/')
def home():
    return 'Home'

@app.route('/dashboard')
def dashboard():
    return 'Dashboard'

@app.route('/listing/<int:listing_id>')
def view_listing(listing_id):
    return f'Listing {listing_id}'

@app.route('/listing/<int:listing_id>/mark-sold', methods=['POST'])
def mark_sold(listing_id):
    return f'Marked {listing_id} as sold'

@app.route('/listing/<int:listing_id>/boost')
def boost_listing(listing_id):
    return f'Boost {listing_id}'

@app.route('/sell')
def sell():
    return 'Sell'

# Setup Jinja2 environment with Flask app context
with app.app_context():
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('my_listings.html')

# Create mock data matching what the route returns
user = {'username': 'testuser', 'email': 'test@example.com'}

active_listings = [
    {
        'id': 1,
        'title': 'iPhone 14 Pro',
        'category': 'Mobiles',
        'subcategory': 'Smartphones',
        'price': 45000,
        'status': 'active',
        'is_sold': False,
        'created_at': datetime.now() - timedelta(days=2),
        'posted_date': datetime.now() - timedelta(days=2),
        'expires_date': datetime.now() + timedelta(days=3),
        'view_count': 12,
        'listing_type': 'standard',
        'boost_type': None,
        'days_left': 3,
        'expired': False
    }
]

expired_listings = [
    {
        'id': 2,
        'title': 'Samsung Galaxy S21',
        'category': 'Mobiles',
        'subcategory': 'Smartphones',
        'price': 35000,
        'status': 'expired',
        'is_sold': False,
        'created_at': datetime.now() - timedelta(days=10),
        'posted_date': datetime.now() - timedelta(days=10),
        'expires_date': datetime.now() - timedelta(days=2),
        'view_count': 5,
        'listing_type': 'standard',
        'boost_type': None,
        'days_expired': 2,
        'expired': True
    }
]

sold_listings = [
    {
        'id': 3,
        'title': 'OnePlus 11',
        'category': 'Mobiles',
        'subcategory': 'Smartphones',
        'price': 38000,
        'status': 'sold',
        'is_sold': True,
        'created_at': datetime.now() - timedelta(days=15),
        'posted_date': datetime.now() - timedelta(days=15),
        'expires_date': datetime.now() - timedelta(days=8),
        'view_count': 8,
        'listing_type': 'standard',
        'boost_type': None,
        'expired': True,
        'sold_date': datetime.now() - timedelta(days=1)
    }
]

    # Try to render the template
    try:
        html = template.render(
            user=user,
            active_listings=active_listings,
            expired_listings=expired_listings,
            sold_listings=sold_listings,
            total_listings=len(active_listings) + len(expired_listings) + len(sold_listings),
            url_for=url_for
        )
    
    print("✅ my_listings.html template rendered successfully!")
    print(f"   - Active listings: {len(active_listings)}")
    print(f"   - Expired listings: {len(expired_listings)}")
    print(f"   - Sold listings: {len(sold_listings)}")
    print(f"   - Total: {len(active_listings) + len(expired_listings) + len(sold_listings)}")
    
    # Verify key elements are present
    checks = [
        ("Active tab exists", "Active ({})".format(len(active_listings)) in html),
        ("Expired tab exists", "Expired ({})".format(len(expired_listings)) in html),
        ("Sold tab exists", "Sold ({})".format(len(sold_listings)) in html),
        ("iPhone title present", "iPhone 14 Pro" in html),
        ("Samsung title present", "Samsung Galaxy S21" in html),
        ("OnePlus title present", "OnePlus 11" in html),
        ("Boost button for expired items", "Boost" in html),
        ("View button exists", "View" in html),
        ("Mark Sold button exists", "Mark Sold" in html),
    ]
    
    print("\n📋 Template Content Checks:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ All checks passed! Template is ready for production.")
        sys.exit(0)
    else:
        print("\n⚠️ Some checks failed. Please review template.")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Template rendering failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
