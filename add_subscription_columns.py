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

    # Add subscription related columns to users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN subscription_start DATETIME NULL")
        print("✅ Added 'subscription_start' column to users")
    except Error as e:
        if "Duplicate column" in str(e):
            print("⚠️  'subscription_start' column already exists")
        else:
            print(f"❌ Error adding subscription_start column: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN subscription_end DATETIME NULL")
        print("✅ Added 'subscription_end' column to users")
    except Error as e:
        if "Duplicate column" in str(e):
            print("⚠️  'subscription_end' column already exists")
        else:
            print(f"❌ Error adding subscription_end column: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN seller_active TINYINT(1) DEFAULT 0")
        print("✅ Added 'seller_active' column to users")
    except Error as e:
        if "Duplicate column" in str(e):
            print("⚠️  'seller_active' column already exists")
        else:
            print(f"❌ Error adding seller_active column: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    # now create a payments table to track subscriptions
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )
    cursor = conn.cursor()
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
                FOREIGN KEY (user_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("✅ seller_payments table ready")
    except Error as e:
        print(f"❌ Error creating seller_payments table: {e}")
    finally:
        cursor.close()
        conn.close()

except Error as e:
    print(f"❌ Database Error: {e}")
