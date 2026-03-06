import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor()

try:
    # Add missing OLX columns to users table
    sql_commands = [
        ("total_listings", "ALTER TABLE users ADD COLUMN total_listings INT DEFAULT 0"),
        ("completed_sales", "ALTER TABLE users ADD COLUMN completed_sales INT DEFAULT 0"),
        ("seller_rating", "ALTER TABLE users ADD COLUMN seller_rating DECIMAL(3,2) DEFAULT 0.0"),
        ("total_rating_count", "ALTER TABLE users ADD COLUMN total_rating_count INT DEFAULT 0"),
    ]
    
    for col_name, sql in sql_commands:
        try:
            cursor.execute(sql)
            print(f"✅ Added column to users: {col_name}")
        except Exception as e:
            if "Duplicate column" in str(e):
                print(f"⚠️  Column already exists: {col_name}")
            else:
                print(f"❌ Error adding {col_name}: {str(e)[:80]}")
    
    conn.commit()
    print("\n✅ All user columns added successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    cursor.close()
    conn.close()
