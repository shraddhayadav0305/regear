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
    
    # Add the missing category and subcategory text columns if they don't exist
    try:
        cursor.execute("ALTER TABLE listings ADD COLUMN category VARCHAR(100)")
        print("✅ Added 'category' column")
    except Error as e:
        if "Duplicate column" in str(e):
            print("⚠️  'category' column already exists")
        else:
            print(f"❌ Error adding category column: {e}")
    
    try:
        cursor.execute("ALTER TABLE listings ADD COLUMN subcategory VARCHAR(100)")
        print("✅ Added 'subcategory' column")
    except Error as e:
        if "Duplicate column" in str(e):
            print("⚠️  'subcategory' column already exists")
        else:
            print(f"❌ Error adding subcategory column: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Verify the changes
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )
    cursor = conn.cursor()
    cursor.execute("DESCRIBE listings")
    columns = cursor.fetchall()
    
    print("\n📋 UPDATED LISTINGS TABLE STRUCTURE:")
    print("-" * 60)
    col_names = [col[0] for col in columns]
    if 'category' in col_names and 'subcategory' in col_names:
        print("✅ Both 'category' and 'subcategory' columns are present")
    
    cursor.close()
    conn.close()
    
except Error as e:
    print(f"❌ Database Error: {e}")
