#!/usr/bin/env python3
"""
Migration script to create subscription and transaction tables
Supports seller package subscription system
"""

import mysql.connector
from mysql.connector import Error as MySQLError

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Shra@0303",
    "database": "regear_db"
}

def get_db_connection():
    """Get MySQL database connection"""
    return mysql.connector.connect(**DB_CONFIG)

def create_subscription_tables():
    """Create user_subscriptions and subscription_transactions tables"""
    
    migration_sql = [
        # User Subscriptions Table
        """
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            plan_name VARCHAR(50) NOT NULL,
            ad_limit INT DEFAULT 0,
            ads_used INT DEFAULT 0,
            start_date DATETIME NOT NULL,
            end_date DATETIME NOT NULL,
            status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_status (user_id, status),
            INDEX idx_end_date (end_date)
        )
        """,
        
        # Subscription Transactions Table
        """
        CREATE TABLE IF NOT EXISTS subscription_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            plan_name VARCHAR(50) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            duration_days INT NOT NULL,
            payment_method VARCHAR(50) DEFAULT 'upi',
            payment_status ENUM('pending', 'success', 'failed') DEFAULT 'pending',
            transaction_id VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user (user_id),
            INDEX idx_status (payment_status),
            INDEX idx_created (created_at)
        )
        """,
        
        # Add subscription_id column to ad_boosts if not exists (for tracking subscription boosts)
        """
        ALTER TABLE ad_boosts ADD COLUMN subscription_id INT DEFAULT NULL
        """,
        
        # Reference to subscription in ad_boosts
        """
        ALTER TABLE ad_boosts ADD FOREIGN KEY (subscription_id) REFERENCES user_subscriptions(id) ON DELETE SET NULL
        """
    ]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for idx, sql in enumerate(migration_sql, 1):
            try:
                print(f"Executing migration {idx}...")
                cursor.execute(sql)
                conn.commit()
                print(f"✅ Migration {idx} successful")
            except MySQLError as e:
                # If table/column already exists, continue
                if "already exists" in str(e) or "Duplicate column" in str(e):
                    print(f"⚠️  Migration {idx} skipped (already exists): {str(e)}")
                    conn.commit()
                else:
                    print(f"❌ Migration {idx} failed: {str(e)}")
                    conn.rollback()
                    raise
        
        cursor.close()
        conn.close()
        print("\n✅ All subscriptiontables created successfully!")
        
    except MySQLError as e:
        print(f"❌ Database error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting subscription tables migration...")
    if create_subscription_tables():
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
