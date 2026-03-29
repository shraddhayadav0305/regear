"""
Subscription helper functions for seller packages
Handles subscription activation, validation, and boost limit checking
"""

import mysql.connector
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Shra@0303",
    "database": "regear_db"
}

def get_db_connection():
    """Get MySQL database connection"""
    return mysql.connector.connect(**DB_CONFIG)

def get_user_active_subscription(user_id):
    """Get user's active subscription if any"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM user_subscriptions 
            WHERE user_id = %s AND status = 'active' AND end_date > NOW()
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        
        subscription = cursor.fetchone()
        cursor.close()
        conn.close()
        return subscription
    except Exception as e:
        print(f"Error fetching subscription: {str(e)}")
        return None

def create_user_subscription(user_id, plan_name, duration_days, transaction_id=None):
    """Create a new subscription for user"""
    try:
        # Plan to ad_limit mapping
        plan_limits = {
            'Starter': 5,
            'Growth': 15,
            'Pro': 40,
            'Business': -1,  # -1 = unlimited
        }
        
        ad_limit = plan_limits.get(plan_name, 0)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_subscriptions 
            (user_id, plan_name, ad_limit, ads_used, start_date, end_date, status)
            VALUES (%s, %s, %s, 0, %s, %s, 'active')
        """, (user_id, plan_name, ad_limit, start_date, end_date))
        
        subscription_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return subscription_id
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        return None


def get_plan_details(plan_name):
    """Get plan price and ad limit by name."""
    plan_limits = {
        'Starter': 5,
        'Growth': 15,
        'Pro': 40,
        'Business': -1,
    }
    plan_prices = {
        'Starter': 149,
        'Growth': 299,
        'Pro': 599,
        'Business': 999,
    }
    return {
        'ad_limit': plan_limits.get(plan_name, 0),
        'price': plan_prices.get(plan_name, 0)
    }


def extend_user_subscription(user_id, subscription_id, extension_days):
    """Extend an existing active subscription by number of days."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT end_date FROM user_subscriptions 
            WHERE id=%s AND user_id=%s AND status='active' AND end_date > NOW()
        """, (subscription_id, user_id))
        subscription = cursor.fetchone()
        if not subscription:
            cursor.close()
            conn.close()
            return False

        new_end_date = subscription['end_date'] + timedelta(days=extension_days)
        cursor.execute("""
            UPDATE user_subscriptions 
            SET end_date=%s
            WHERE id=%s AND user_id=%s
        """, (new_end_date, subscription_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error extending subscription: {str(e)}")
        return False


def upgrade_user_subscription(user_id, old_subscription_id, new_plan_name, duration_days):
    """Expire the old subscription and create a new upgraded subscription."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_subscriptions 
            SET status='expired', end_date=NOW() 
            WHERE id=%s AND user_id=%s AND status='active'
        """, (old_subscription_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return create_user_subscription(user_id, new_plan_name, duration_days)
    except Exception as e:
        print(f"Error upgrading subscription: {str(e)}")
        return None


def can_user_boost_ad(user_id):
    """Check if user can boost an ad based on subscription or individual boosts"""
    subscription = get_user_active_subscription(user_id)
    
    if subscription:
        # User has active subscription
        if subscription['ad_limit'] == -1:
            # Unlimited
            return True, "unlimited", None
        elif subscription['ads_used'] < subscription['ad_limit']:
            # Within limit
            remaining = subscription['ad_limit'] - subscription['ads_used']
            return True, subscription['plan_name'], remaining
        else:
            # Limit reached
            return False, subscription['plan_name'], 0
    
    # No subscription, individual boosts still work
    return True, "individual", None

def increment_subscription_boost_count(user_id, subscription_id=None):
    """Increment ads_used count in subscription"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if subscription_id:
            cursor.execute("""
                UPDATE user_subscriptions 
                SET ads_used = ads_used + 1 
                WHERE id = %s AND user_id = %s
            """, (subscription_id, user_id))
        else:
            # Get active subscription and increment
            cursor.execute("""
                UPDATE user_subscriptions 
                SET ads_used = ads_used + 1 
                WHERE user_id = %s AND status = 'active' AND end_date > NOW()
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error incrementing boost count: {str(e)}")
        return False

def mark_expired_subscriptions(user_id):
    """Mark expired subscriptions as expired"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_subscriptions 
            SET status = 'expired' 
            WHERE user_id = %s AND status = 'active' AND end_date <= NOW()
        """, (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error marking expired subscriptions: {str(e)}")
        return False

def get_subscription_info(user_id):
    """Get detailed subscription info for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM user_subscriptions 
            WHERE user_id = %s AND status = 'active'
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        
        subscription = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if subscription:
            remaining = subscription['ad_limit'] - subscription['ads_used'] if subscription['ad_limit'] != -1 else -1
            return {
                'plan_name': subscription['plan_name'],
                'ads_used': subscription['ads_used'],
                'ad_limit': subscription['ad_limit'],
                'remaining': remaining,
                'end_date': subscription['end_date'],
                'status': subscription['status']
            }
        return None
    except Exception as e:
        print(f"Error getting subscription info: {str(e)}")
        return None

def record_subscription_transaction(user_id, plan_name, amount, duration_days, payment_status='success', transaction_id=None, payment_method='upi'):
    """Record subscription transaction"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subscription_transactions 
            (user_id, plan_name, amount, duration_days, payment_method, payment_status, transaction_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, plan_name, amount, duration_days, payment_method, payment_status, transaction_id))
        cursor.execute("""
            INSERT INTO payments 
            (user_id, amount, method, transaction_id, status, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (user_id, amount, payment_method, transaction_id, payment_status))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error recording transaction: {str(e)}")
        return False
