"""
Subscription helper functions for seller packages
Handles subscription activation, validation, and boost limit checking
"""

import mysql.connector
from datetime import datetime, timedelta

from transactions_helpers import (
    map_payment_method,
    map_transaction_status,
    calculate_gst,
    calculate_total
)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Shra@0303",
    "database": "regear_db"
}

PLAN_DETAILS = {
    'Free': {'ad_limit': 1, 'boost_limit': 0, 'price': 0},
    'Starter': {'ad_limit': 5, 'boost_limit': 5, 'price': 149},
    'Growth': {'ad_limit': 15, 'boost_limit': 15, 'price': 299},
    'Pro': {'ad_limit': 50, 'boost_limit': 40, 'price': 599},
    'Business': {'ad_limit': -1, 'boost_limit': -1, 'price': 999}
}

DEFAULT_FREE_PLAN = 'Free'
SUBSCRIPTIONS_TABLE = 'user_subscriptions'
TRANSACTIONS_TABLE = 'subscription_transactions'


def get_db_connection():
    """Get MySQL database connection."""
    return mysql.connector.connect(**DB_CONFIG)


def column_exists(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (table_name, column_name)
    )
    return cursor.fetchone()[0] > 0


def ensure_subscription_tables(cursor):
    """Ensure subscription-related tables and columns exist."""
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {SUBSCRIPTIONS_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            plan_name VARCHAR(50) NOT NULL,
            ad_limit INT DEFAULT 0,
            ads_used INT DEFAULT 0,
            boost_limit INT DEFAULT 0,
            boosts_used INT DEFAULT 0,
            start_date DATETIME NOT NULL,
            end_date DATETIME NOT NULL,
            status ENUM('active','expired','cancelled') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_status (user_id, status),
            INDEX idx_end_date (end_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TRANSACTIONS_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            plan_name VARCHAR(50) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            duration_days INT NOT NULL,
            payment_method VARCHAR(50) DEFAULT 'upi',
            payment_status ENUM('pending','success','failed') DEFAULT 'pending',
            transaction_id VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user (user_id),
            INDEX idx_status (payment_status),
            INDEX idx_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    if not column_exists(cursor, SUBSCRIPTIONS_TABLE, 'boost_limit'):
        cursor.execute(f"ALTER TABLE {SUBSCRIPTIONS_TABLE} ADD COLUMN boost_limit INT DEFAULT 0")
    if not column_exists(cursor, SUBSCRIPTIONS_TABLE, 'boosts_used'):
        cursor.execute(f"ALTER TABLE {SUBSCRIPTIONS_TABLE} ADD COLUMN boosts_used INT DEFAULT 0")


def normalize_subscription_row(subscription):
    if not subscription:
        return None
    plan_name = subscription.get('plan_name', DEFAULT_FREE_PLAN)
    plan_defaults = PLAN_DETAILS.get(plan_name, {})
    subscription['ad_limit'] = int(subscription.get('ad_limit', plan_defaults.get('ad_limit', 0)))
    subscription['ads_used'] = int(subscription.get('ads_used', 0))
    subscription['boost_limit'] = int(subscription.get('boost_limit', plan_defaults.get('boost_limit', subscription['ad_limit'])))
    subscription['boosts_used'] = int(subscription.get('boosts_used', subscription['ads_used']))
    if subscription['boost_limit'] == 0 and plan_name != DEFAULT_FREE_PLAN:
        subscription['boost_limit'] = subscription['ad_limit']
    return subscription


def get_user_active_subscription(user_id):
    """Get the user's currently active subscription."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        ensure_subscription_tables(cursor)
        cursor.execute(
            f"""
            SELECT * FROM {SUBSCRIPTIONS_TABLE}
            WHERE user_id = %s AND status = 'active' AND end_date > NOW()
            ORDER BY start_date DESC LIMIT 1
            """,
            (user_id,)
        )
        subscription = normalize_subscription_row(cursor.fetchone())
        cursor.close()
        conn.close()
        return subscription
    except Exception as e:
        print(f"Error fetching subscription: {str(e)}")
        return None


def get_or_create_free_subscription(user_id):
    """Return or create a default free subscription for a user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        ensure_subscription_tables(cursor)
        cursor.execute(
            f"""
            SELECT * FROM {SUBSCRIPTIONS_TABLE}
            WHERE user_id = %s AND plan_name = %s AND status = 'active'
            ORDER BY start_date DESC LIMIT 1
            """,
            (user_id, DEFAULT_FREE_PLAN)
        )
        subscription = cursor.fetchone()
        if subscription:
            subscription = normalize_subscription_row(subscription)
            cursor.close()
            conn.close()
            return subscription

        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        cursor.execute(
            f"""
            INSERT INTO {SUBSCRIPTIONS_TABLE}
            (user_id, plan_name, ad_limit, ads_used, boost_limit, boosts_used, start_date, end_date, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'active')
            """,
            (
                user_id,
                DEFAULT_FREE_PLAN,
                PLAN_DETAILS[DEFAULT_FREE_PLAN]['ad_limit'],
                0,
                PLAN_DETAILS[DEFAULT_FREE_PLAN]['boost_limit'],
                0,
                start_date,
                end_date,
            )
        )
        conn.commit()
        subscription_id = cursor.lastrowid
        cursor.execute(f"SELECT * FROM {SUBSCRIPTIONS_TABLE} WHERE id=%s", (subscription_id,))
        subscription = normalize_subscription_row(cursor.fetchone())
        cursor.close()
        conn.close()
        return subscription
    except Exception as e:
        print(f"Error creating free subscription: {str(e)}")
        return None


def can_user_post_ad(user_id):
    """Return whether the user may post a new ad under subscription rules."""
    subscription = get_user_active_subscription(user_id)
    if not subscription:
        subscription = get_or_create_free_subscription(user_id)
    if not subscription:
        return False, None, "Unable to determine subscription status."
    if subscription['status'] != 'active':
        return False, subscription, "Your plan has expired."
    if subscription['ad_limit'] >= 0 and subscription['ads_used'] >= subscription['ad_limit']:
        return False, subscription, "Ad limit reached. Please purchase a plan."
    return True, subscription, None


def increment_subscription_ads_count(user_id, subscription_id=None):
    """Increment the user's ads_used counter for the active subscription."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        ensure_subscription_tables(cursor)
        if subscription_id:
            cursor.execute(
                f"""
                UPDATE {SUBSCRIPTIONS_TABLE}
                SET ads_used = ads_used + 1
                WHERE id = %s AND user_id = %s
                """,
                (subscription_id, user_id)
            )
        else:
            cursor.execute(
                f"""
                UPDATE {SUBSCRIPTIONS_TABLE}
                SET ads_used = ads_used + 1
                WHERE user_id = %s AND status = 'active' AND end_date > NOW()
                ORDER BY start_date DESC LIMIT 1
                """,
                (user_id,)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error incrementing ad count: {str(e)}")
        return False


def can_user_boost_ad(user_id):
    """Return whether the user may use a subscription boost."""
    subscription = get_user_active_subscription(user_id)
    if not subscription:
        return False, None, "No active subscription found. Please purchase a plan."

    if subscription['plan_name'] == DEFAULT_FREE_PLAN:
        return False, subscription, "Your free plan does not include boosted listings. Purchase a subscription to enable boosts."

    if subscription['boost_limit'] >= 0 and subscription['boosts_used'] >= subscription['boost_limit']:
        return False, subscription, "Boost limit reached. Upgrade your plan or wait for renewal."

    return True, subscription, None


def increment_subscription_boost_count(user_id, subscription_id=None):
    """Increment the subscription boost usage counter."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        ensure_subscription_tables(cursor)
        if subscription_id:
            cursor.execute(
                f"""
                UPDATE {SUBSCRIPTIONS_TABLE}
                SET boosts_used = boosts_used + 1
                WHERE id = %s AND user_id = %s
                """,
                (subscription_id, user_id)
            )
        else:
            cursor.execute(
                f"""
                UPDATE {SUBSCRIPTIONS_TABLE}
                SET boosts_used = boosts_used + 1
                WHERE user_id = %s AND status = 'active' AND end_date > NOW()
                ORDER BY start_date DESC LIMIT 1
                """,
                (user_id,)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error incrementing boost count: {str(e)}")
        return False


def mark_expired_subscriptions(user_id=None):
    """Mark expired subscriptions as expired."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        ensure_subscription_tables(cursor)
        if user_id:
            cursor.execute(
                f"""
                UPDATE {SUBSCRIPTIONS_TABLE}
                SET status = 'expired'
                WHERE user_id = %s AND status = 'active' AND end_date <= NOW()
                """,
                (user_id,)
            )
        else:
            cursor.execute(
                f"""
                UPDATE {SUBSCRIPTIONS_TABLE}
                SET status = 'expired'
                WHERE status = 'active' AND end_date <= NOW()
                """
            )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error marking expired subscriptions: {str(e)}")
        return False


def create_user_subscription(user_id, plan_name, duration_days, transaction_id=None):
    """Create a new subscription for the user."""
    try:
        normalized_plan_name = normalize_plan_name(plan_name)
        plan = get_plan_details(normalized_plan_name)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        conn = get_db_connection()
        cursor = conn.cursor()
        ensure_subscription_tables(cursor)
        cursor.execute(
            f"""
            INSERT INTO {SUBSCRIPTIONS_TABLE}
            (user_id, plan_name, ad_limit, ads_used, boost_limit, boosts_used, start_date, end_date, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'active')
            """,
            (
                user_id,
                normalized_plan_name,
                plan['ad_limit'],
                0,
                plan['boost_limit'],
                0,
                start_date,
                end_date
            )
        )
        subscription_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return subscription_id
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        return None


def normalize_plan_name(plan_name):
    """Normalize a subscription plan name for case-insensitive matching."""
    if not plan_name or not isinstance(plan_name, str):
        return DEFAULT_FREE_PLAN
    cleaned = plan_name.strip()
    if cleaned in PLAN_DETAILS:
        return cleaned
    lowered = cleaned.lower()
    for known_name in PLAN_DETAILS:
        if known_name.lower() == lowered:
            return known_name
    return cleaned


def get_plan_details(plan_name):
    """Return plan metadata for a plan name."""
    normalized_plan_name = normalize_plan_name(plan_name)
    return PLAN_DETAILS.get(normalized_plan_name, {'ad_limit': 0, 'boost_limit': 0, 'price': 0})


def extend_user_subscription(user_id, subscription_id, extension_days, reset_usage=False):
    """Extend an existing active subscription by a number of days."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        ensure_subscription_tables(cursor)
        cursor.execute(
            f"""
            SELECT end_date FROM {SUBSCRIPTIONS_TABLE}
            WHERE id=%s AND user_id=%s AND status='active' AND end_date > NOW()
            """,
            (subscription_id, user_id)
        )
        subscription = cursor.fetchone()
        if not subscription:
            cursor.close()
            conn.close()
            return False

        new_end_date = subscription['end_date'] + timedelta(days=extension_days)
        if reset_usage:
            cursor.execute(
                f"""
                UPDATE {SUBSCRIPTIONS_TABLE}
                SET end_date=%s, ads_used=0, boosts_used=0
                WHERE id=%s AND user_id=%s
                """,
                (new_end_date, subscription_id, user_id)
            )
        else:
            cursor.execute(
                f"""
                UPDATE {SUBSCRIPTIONS_TABLE}
                SET end_date=%s
                WHERE id=%s AND user_id=%s
                """,
                (new_end_date, subscription_id, user_id)
            )
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
        ensure_subscription_tables(cursor)
        cursor.execute(
            f"""
            UPDATE {SUBSCRIPTIONS_TABLE}
            SET status='expired', end_date=NOW()
            WHERE id=%s AND user_id=%s AND status='active'
            """,
            (old_subscription_id, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return create_user_subscription(user_id, new_plan_name, duration_days)
    except Exception as e:
        print(f"Error upgrading subscription: {str(e)}")
        return None


def get_subscription_info(user_id):
    """Return the current subscription details for dashboard and analytics."""
    try:
        mark_expired_subscriptions(user_id)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT * FROM {SUBSCRIPTIONS_TABLE}
            WHERE user_id = %s AND status = 'active'
            ORDER BY start_date DESC LIMIT 1
            """,
            (user_id,)
        )
        subscription = normalize_subscription_row(cursor.fetchone())
        cursor.close()
        conn.close()

        if not subscription:
            return None

        remaining_ads = subscription['ad_limit'] - subscription['ads_used'] if subscription['ad_limit'] != -1 else -1
        remaining_boosts = subscription['boost_limit'] - subscription['boosts_used'] if subscription['boost_limit'] != -1 else -1
        return {
            'plan_name': subscription['plan_name'],
            'ads_used': subscription['ads_used'],
            'ad_limit': subscription['ad_limit'],
            'boosts_used': subscription['boosts_used'],
            'boost_limit': subscription['boost_limit'],
            'remaining_ads': remaining_ads,
            'remaining_boosts': remaining_boosts,
            'start_date': subscription['start_date'],
            'end_date': subscription['end_date'],
            'status': subscription['status']
        }
    except Exception as e:
        print(f"Error getting subscription info: {str(e)}")
        return None


def ensure_transactions_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            type ENUM('subscription','boost') NOT NULL,
            reference_id INT NULL,
            base_amount DECIMAL(10,2) NOT NULL,
            gst_amount DECIMAL(10,2) NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            payment_method ENUM('UPI','Card','Wallet') NOT NULL,
            status ENUM('completed','failed','refunded') NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_transactions_status (status),
            INDEX idx_transactions_type (type),
            INDEX idx_transactions_payment_method (payment_method),
            INDEX idx_transactions_created_at (created_at)
        )
    """)


def record_subscription_transaction(user_id, plan_name, amount, duration_days, payment_status='success', transaction_id=None, payment_method='upi'):
    """Record subscription transaction and canonical transaction entry."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subscription_transactions 
            (user_id, plan_name, amount, duration_days, payment_method, payment_status, transaction_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, plan_name, amount, duration_days, payment_method, payment_status, transaction_id))
        subscription_tx_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO payments 
            (user_id, amount, method, transaction_id, status, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (user_id, amount, payment_method, transaction_id, payment_status))

        try:
            ensure_transactions_table(cursor)
            gst_amount = calculate_gst(amount)
            total_amount = calculate_total(amount)
            payment_method_clean = map_payment_method(payment_method)
            status_clean = map_transaction_status(payment_status)
            cursor.execute("""
                INSERT INTO transactions
                (user_id, type, reference_id, base_amount, gst_amount, total_amount, payment_method, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (user_id, 'subscription', subscription_tx_id, float(amount), gst_amount, total_amount, payment_method_clean, status_clean))
        except Exception:
            pass

        conn.commit()
        cursor.close()
        conn.close()
        return subscription_tx_id
    except Exception as e:
        print(f"Error recording transaction: {str(e)}")
        return None
