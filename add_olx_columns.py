import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor()

try:
    # Add missing OLX columns to listings table (without IF NOT EXISTS)
    sql_commands = [
        ("posted_date", "ALTER TABLE listings ADD COLUMN posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER created_at"),
        ("expires_date", "ALTER TABLE listings ADD COLUMN expires_date TIMESTAMP AFTER posted_date"),
        ("is_sold", "ALTER TABLE listings ADD COLUMN is_sold BOOLEAN DEFAULT FALSE AFTER expires_date"),
        ("sold_date", "ALTER TABLE listings ADD COLUMN sold_date TIMESTAMP AFTER is_sold"),
        ("view_count", "ALTER TABLE listings ADD COLUMN view_count INT DEFAULT 0 AFTER sold_date"),
        ("listing_type", "ALTER TABLE listings ADD COLUMN listing_type VARCHAR(50) DEFAULT 'free_trial' AFTER view_count"),
        ("boost_type", "ALTER TABLE listings ADD COLUMN boost_type VARCHAR(50) AFTER listing_type"),
        ("boost_expires_date", "ALTER TABLE listings ADD COLUMN boost_expires_date TIMESTAMP AFTER boost_type"),
    ]
    
    for col_name, sql in sql_commands:
        try:
            cursor.execute(sql)
            print(f"✅ Added column: {col_name}")
        except Exception as e:
            if "Duplicate column" in str(e):
                print(f"⚠️  Column already exists: {col_name}")
            else:
                print(f"❌ Error adding {col_name}: {str(e)[:80]}")
    
    conn.commit()
    print("\n✅ Column addition phase complete!")
    
    # Set expires_date for existing listings (5 days from creation)
    cursor.execute("""
        UPDATE listings 
        SET expires_date = DATE_ADD(created_at, INTERVAL 5 DAY)
        WHERE expires_date IS NULL OR expires_date = '0000-00-00 00:00:00'
    """)
    updated = cursor.rowcount
    conn.commit()
    print(f"✅ Set expires_date for {updated} existing listings")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    cursor.close()
    conn.close()
