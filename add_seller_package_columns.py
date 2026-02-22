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

    # Add seller_package and registration_fee columns to users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN seller_package VARCHAR(50) NULL")
        print("✅ Added 'seller_package' column to users")
    except Error as e:
        if "Duplicate column" in str(e):
            print("⚠️  'seller_package' column already exists")
        else:
            print(f"❌ Error adding seller_package column: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN registration_fee DECIMAL(10,2) NULL")
        print("✅ Added 'registration_fee' column to users")
    except Error as e:
        if "Duplicate column" in str(e):
            print("⚠️  'registration_fee' column already exists")
        else:
            print(f"❌ Error adding registration_fee column: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    # verify structure
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )
    cursor = conn.cursor()
    cursor.execute("DESCRIBE users")
    cols = cursor.fetchall()
    print("\n📋 users table columns:")
    for col in cols:
        print(f" - {col[0]} ({col[1]})")
    cursor.close()
    conn.close()

except Error as e:
    print(f"❌ Database Error: {e}")
