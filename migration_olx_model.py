"""
Database Migration Script for ReGear OLX Model Redesign
Updates existing schema and creates new tables for:
- Free trial selling system
- Product expiration tracking
- Boost/Feature purchases
- Reviews and ratings
- Chat system
- Product reports
"""

import mysql.connector
from mysql.connector import Error as MySQLError
import os
from datetime import datetime

def get_db_connection():
    """Create database connection"""
    host = os.environ.get('REGEAR_DB_HOST', 'localhost')
    user = os.environ.get('REGEAR_DB_USER', 'root')
    password = os.environ.get('REGEAR_DB_PASSWORD', 'Shra@0303')
    database = os.environ.get('REGEAR_DB_NAME', 'regear_db')
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def execute_script(cursor, sql_statements):
    """Execute multiple SQL statements safely"""
    for statement in sql_statements:
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                cursor.execute(statement)
                print(f"✅ Executed: {statement[:80]}...")
            except MySQLError as e:
                print(f"⚠️  Error (may be expected if already exists): {e}")
                print(f"   Statement: {statement[:100]}...")

def migrate_database():
    """Run all migration steps"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("ReGear Database Migration - OLX Model")
    print("="*60 + "\n")
    
    try:
        # ===== STEP 1: Update users table =====
        print("\n📝 Step 1: Updating users table...")
        users_updates = [
            """ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20) AFTER email""",
            """ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)""",
            """ALTER TABLE users ADD COLUMN IF NOT EXISTS total_listings INT DEFAULT 0""",
            """ALTER TABLE users ADD COLUMN IF NOT EXISTS completed_sales INT DEFAULT 0""",
            """ALTER TABLE users ADD COLUMN IF NOT EXISTS seller_rating DECIMAL(3,2) DEFAULT 0""",
            """ALTER TABLE users ADD COLUMN IF NOT EXISTS total_rating_count INT DEFAULT 0""",
            """ALTER TABLE users MODIFY COLUMN role ENUM('user', 'admin', 'blocked') DEFAULT 'user'""",
        ]
        execute_script(cursor, users_updates)
        
        # ===== STEP 2: Update listings table =====
        print("\n📝 Step 2: Updating listings table...")
        listings_updates = [
            """ALTER TABLE listings ADD COLUMN IF NOT EXISTS posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP""",
            """ALTER TABLE listings ADD COLUMN IF NOT EXISTS expires_date TIMESTAMP NULL""",
            """ALTER TABLE listings ADD COLUMN IF NOT EXISTS is_sold BOOLEAN DEFAULT FALSE""",
            """ALTER TABLE listings ADD COLUMN IF NOT EXISTS sold_date TIMESTAMP NULL""",
            """ALTER TABLE listings ADD COLUMN IF NOT EXISTS view_count INT DEFAULT 0""",
            """ALTER TABLE listings ADD COLUMN IF NOT EXISTS boost_type VARCHAR(50) NULL""",
            """ALTER TABLE listings ADD COLUMN IF NOT EXISTS boost_expires_date TIMESTAMP NULL""",
            """ALTER TABLE listings ADD COLUMN IF NOT EXISTS listing_type ENUM('free_trial', 'boosted', 'featured', 'premium') DEFAULT 'free_trial'""",
            """ALTER TABLE listings MODIFY COLUMN status ENUM('active', 'expired', 'sold', 'boosted', 'featured', 'archived') DEFAULT 'active'""",
        ]
        execute_script(cursor, listings_updates)
        
        # ===== STEP 3: Create product_boosts table =====
        print("\n📝 Step 3: Creating product_boosts table...")
        create_boosts = """
            CREATE TABLE IF NOT EXISTS product_boosts (
              id INT AUTO_INCREMENT PRIMARY KEY,
              listing_id INT NOT NULL,
              user_id INT NOT NULL,
              boost_type VARCHAR(50) NOT NULL,
              price DECIMAL(10,2) NOT NULL,
              days_active INT NOT NULL,
              purchased_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              expires_date TIMESTAMP,
              is_active BOOLEAN DEFAULT TRUE,
              FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
              INDEX idx_user_active (user_id, is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_boosts)
        print("✅ product_boosts table created")
        
        # ===== STEP 4: Create product_reviews table =====
        print("\n📝 Step 4: Creating product_reviews table...")
        create_reviews = """
            CREATE TABLE IF NOT EXISTS product_reviews (
              id INT AUTO_INCREMENT PRIMARY KEY,
              listing_id INT NOT NULL,
              buyer_id INT NOT NULL,
              seller_id INT NOT NULL,
              rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
              review_text TEXT,
              created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
              FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
              FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
              INDEX idx_seller (seller_id),
              INDEX idx_listing (listing_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_reviews)
        print("✅ product_reviews table created")
        
        # ===== STEP 5: Create product_reports table =====
        print("\n📝 Step 5: Creating product_reports table...")
        create_reports = """
            CREATE TABLE IF NOT EXISTS product_reports (
              id INT AUTO_INCREMENT PRIMARY KEY,
              listing_id INT NOT NULL,
              reporter_id INT NOT NULL,
              reason VARCHAR(255) NOT NULL,
              description TEXT,
              status ENUM('pending', 'reviewed', 'removed', 'false_report') DEFAULT 'pending',
              reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
              FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
              INDEX idx_listing_status (listing_id, status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_reports)
        print("✅ product_reports table created")
        
        # ===== STEP 6: Create chats table =====
        print("\n📝 Step 6: Creating chats table...")
        create_chats = """
            CREATE TABLE IF NOT EXISTS chats (
              id INT AUTO_INCREMENT PRIMARY KEY,
              listing_id INT NOT NULL,
              buyer_id INT NOT NULL,
              seller_id INT NOT NULL,
              created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              last_message_date TIMESTAMP NULL,
              FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
              FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
              FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
              UNIQUE KEY unique_chat (listing_id, buyer_id, seller_id),
              INDEX idx_buyer (buyer_id),
              INDEX idx_seller (seller_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_chats)
        print("✅ chats table created")
        
        # ===== STEP 7: Create chat_messages table =====
        print("\n📝 Step 7: Creating chat_messages table...")
        create_messages = """
            CREATE TABLE IF NOT EXISTS chat_messages (
              id INT AUTO_INCREMENT PRIMARY KEY,
              chat_id INT NOT NULL,
              sender_id INT NOT NULL,
              message_text TEXT,
              sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              is_read BOOLEAN DEFAULT FALSE,
              FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
              FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
              INDEX idx_chat_read (chat_id, is_read)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_messages)
        print("✅ chat_messages table created")
        
        # Commit all changes
        conn.commit()
        print("\n" + "="*60)
        print("✅ Database migration completed successfully!")
        print("="*60 + "\n")
        
    except MySQLError as e:
        print(f"\n❌ Migration error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        exit(1)
