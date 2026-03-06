#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )
    cursor = conn.cursor()

    # Add subscription columns if not present
    columns_to_add = {
        "seller_active": "TINYINT DEFAULT 0",
        "subscription_start": "TIMESTAMP NULL",
        "subscription_end": "TIMESTAMP NULL"
    }
    
    for col_name, col_def in columns_to_add.items():
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
            print(f"✅ Added '{col_name}' column to users")
            conn.commit()
        except Error as e:
            if "Duplicate column" in str(e):
                print(f"⚠️  '{col_name}' column already exists")
            else:
                print(f"❌ Error: {e}")

    # Create seller_payments table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seller_payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                plan VARCHAR(50),
                amount DECIMAL(10,2),
                gst DECIMAL(10,2),
                total_amount DECIMAL(10,2),
                payment_method VARCHAR(50),
                paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_paid_at (paid_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ seller_payments table created")
        conn.commit()
    except Exception as e:
        if "already exists" in str(e):
            print("⚠️  seller_payments table already exists")

    cursor.close()
    conn.close()
    print("\n✅ Database setup complete!")

except Exception as e:
    print(f"❌ Error: {e}")
