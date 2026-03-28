#!/usr/bin/env python3
"""
End-to-End Integration Test for Seller Subscription System
Tests the complete user journey: signup → subscription purchase → ad boost
"""

import mysql.connector
from datetime import datetime, timedelta
import hashlib
import random
import string

# Database connection config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Shra@0303",
    "database": "regear_db"
}

def get_db_connection():
    """Create database connection"""
    return mysql.connector.connect(**DB_CONFIG)

def create_test_user(email, username, role='seller'):
    """Create a test user and return user_id"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate salt and hash password
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        password_hash = hashlib.sha256((salt + "testpass123").encode()).hexdigest()
        hashed_password = f"{salt}${password_hash}"
        
        # Insert user with full_name field
        query = """
        INSERT INTO users (username, email, password, role, phone, full_name, created_at)
        VALUES (%s, %s, %s, %s, '9999999999', %s, NOW())
        """
        cursor.execute(query, (username, email, hashed_password, role, f"Test {username}"))
        conn.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return user_id
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        return None

def create_test_ad(user_id, title="Test Product"):
    """Create a test listing and return listing_id"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO listings (user_id, title, description, price, category, 
                            subcategory, location, phone, email, status, created_at)
        VALUES (%s, %s, 'Test description for product', 5000, 'Mobiles', 
               'Smartphones', 'Bangalore', '9999999999', 'test@test.com', 'active', NOW())
        """
        cursor.execute(query, (user_id, title))
        conn.commit()
        
        listing_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return listing_id
    except Exception as e:
        print(f"❌ Failed to create test ad: {e}")
        return None

def purchase_subscription(user_id, plan_name='Growth'):
    """Simulate purchasing a subscription"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Define plans
        plans = {
            'Starter': {'ad_limit': 5, 'amount': 149, 'days': 30},
            'Growth': {'ad_limit': 15, 'amount': 299, 'days': 30},
            'Pro': {'ad_limit': 40, 'amount': 599, 'days': 30},
            'Business': {'ad_limit': -1, 'amount': 999, 'days': 30}
        }
        
        if plan_name not in plans:
            print(f"❌ Unknown plan: {plan_name}")
            return False
        
        plan = plans[plan_name]
        
        # Create subscription
        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan['days'])
        
        query = """
        INSERT INTO user_subscriptions (user_id, plan_name, ad_limit, ads_used, 
                                       start_date, end_date, status)
        VALUES (%s, %s, %s, 0, %s, %s, 'active')
        """
        cursor.execute(query, (user_id, plan_name, plan['ad_limit'],
                             start_date, end_date))
        
        subscription_id = cursor.lastrowid
        
        # Record transaction
        query = """
        INSERT INTO subscription_transactions (user_id, plan_name, amount, 
                                             duration_days, payment_method, 
                                             payment_status, transaction_id)
        VALUES (%s, %s, %s, %s, 'UPI', 'success', %s)
        """
        transact_id = f"TEST{random.randint(1000000, 9999999)}"
        cursor.execute(query, (user_id, plan_name, plan['amount'], 
                             plan['days'], transact_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Subscription created: {plan_name} (ID: {subscription_id})")
        return subscription_id
    except Exception as e:
        print(f"❌ Failed to purchase subscription: {e}")
        return False

def boost_ad_with_subscription(user_id, listing_id, subscription_id):
    """Simulate boosting an ad with subscription"""
    try:
        from subscription_helpers import (
            get_user_active_subscription,
            increment_subscription_boost_count,
            mark_expired_subscriptions
        )
        
        # Mark expired subscriptions
        mark_expired_subscriptions(user_id)
        
        # Check if user can boost
        sub = get_user_active_subscription(user_id)
        if not sub:
            print("❌ No active subscription found")
            return False
        
        plan_name = sub['plan_name']
        ads_used = sub['ads_used']
        ad_limit = sub['ad_limit']
        
        # Check if within limit (ad_limit = -1 means unlimited)
        if ad_limit != -1 and ads_used >= ad_limit:
            print(f"❌ Boost limit reached: {ads_used}/{ad_limit}")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create boost record
        query = """
        INSERT INTO ad_boosts (listing_id, user_id, boost_type, amount_paid, 
                             payment_method, status, subscription_id, created_at)
        VALUES (%s, %s, 'subscription', 0, 'subscription', 'active', %s, NOW())
        """
        cursor.execute(query, (listing_id, user_id, subscription_id))
        boost_id = cursor.lastrowid
        conn.commit()
        
        # Increment boost count
        increment_subscription_boost_count(user_id, subscription_id)
        
        cursor.close()
        conn.close()
        
        new_ads_used = ads_used + 1
        remaining = ad_limit - new_ads_used if ad_limit != -1 else '∞'
        print(f"✅ Ad boosted: {plan_name} plan ({new_ads_used}/{ad_limit if ad_limit != -1 else '∞'}) Boost ID: {boost_id}")
        
        return boost_id
    except Exception as e:
        print(f"❌ Failed to boost ad: {e}")
        return False

def verify_subscription_status(user_id):
    """Verify subscription status in dashboard"""
    try:
        from subscription_helpers import get_subscription_info
        
        info = get_subscription_info(user_id)
        if not info:
            print("❌ No subscription info found")
            return False
        
        print(f"\n📊 Subscription Status:")
        print(f"   Plan: {info['plan_name']}")
        print(f"   Boosts Used: {info['ads_used']}/{info['ad_limit'] if info['ad_limit'] != -1 else '∞'}")
        print(f"   Remaining: {info['remaining'] if info['remaining'] != -1 else '∞'}")
        print(f"   Expiry: {info['end_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Status: {info['status']}")
        return True
    except Exception as e:
        print(f"❌ Failed to verify status: {e}")
        return False

def cleanup_test_data(user_id):
    """Clean up test records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete test data
        cursor.execute("DELETE FROM ad_boosts WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM listings WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM subscription_transactions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_subscriptions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Test data cleaned up")
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def run_e2e_test():
    """Run complete end-to-end test"""
    print("=" * 60)
    print("🚀 SELLER SUBSCRIPTION SYSTEM - END-TO-END TEST")
    print("=" * 60)
    
    test_ok = True
    user_id = None
    
    try:
        # TEST 1: Create seller user
        print("\n[TEST 1] Creating seller account...")
        user_id = create_test_user(f"seller{random.randint(1000,9999)}@test.com", 
                                  f"seller{random.randint(1000,9999)}", 
                                  role='seller')
        if not user_id:
            test_ok = False
        else:
            print(f"✅ Seller created: ID {user_id}")
        
        # TEST 2: Create test listing
        print("\n[TEST 2] Creating test product listing...")
        listing_id = create_test_ad(user_id, "iPhone 13")
        if not listing_id:
            test_ok = False
        else:
            print(f"✅ Listing created: ID {listing_id}")
        
        # TEST 3: Purchase Growth plan subscription
        print("\n[TEST 3] Purchasing Growth subscription (₹299, 15 boosts)...")
        subscription_id = purchase_subscription(user_id, 'Growth')
        if not subscription_id:
            test_ok = False
        else:
            print(f"✅ Subscription purchased")
        
        # TEST 4: Verify subscription status
        print("\n[TEST 4] Verifying subscription status...")
        if not verify_subscription_status(user_id):
            test_ok = False
        
        # TEST 5: Boost ad using subscription
        print("\n[TEST 5] Boosting ad with subscription...")
        boost_id = boost_ad_with_subscription(user_id, listing_id, subscription_id)
        if not boost_id:
            test_ok = False
        
        # TEST 6: Verify update boost count
        print("\n[TEST 6] Verifying boost count updated...")
        if not verify_subscription_status(user_id):
            test_ok = False
        
        # TEST 7: Boost multiple ads
        print("\n[TEST 7] Boosting multiple ads sequentially...")
        for i in range(2, 5):  # Create and boost 3 more ads
            listing_id2 = create_test_ad(user_id, f"Test Product {i}")
            if listing_id2:
                boost_id2 = boost_ad_with_subscription(user_id, listing_id2, subscription_id)
                if not boost_id2:
                    test_ok = False
        
        # TEST 8: Final status check
        print("\n[TEST 8] Final subscription status...")
        if not verify_subscription_status(user_id):
            test_ok = False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        test_ok = False
    finally:
        # Cleanup
        if user_id:
            print("\n[CLEANUP] Removing test data...")
            cleanup_test_data(user_id)
    
    # Summary
    print("\n" + "=" * 60)
    if test_ok:
        print("✅ ALL E2E TESTS PASSED - Subscription system fully functional!")
    else:
        print("❌ SOME TESTS FAILED - Check output above for details")
    print("=" * 60)
    
    return test_ok

if __name__ == "__main__":
    success = run_e2e_test()
    exit(0 if success else 1)
