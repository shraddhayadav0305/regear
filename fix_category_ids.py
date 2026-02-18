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
    
    # Make category_id and subcategory_id nullable with NULL default
    try:
        cursor.execute("ALTER TABLE listings MODIFY COLUMN category_id INT NULL DEFAULT NULL")
        print("✅ Modified 'category_id' to be nullable")
    except Error as e:
        print(f"⚠️  category_id modification: {e}")
    
    try:
        cursor.execute("ALTER TABLE listings MODIFY COLUMN subcategory_id INT NULL DEFAULT NULL")
        print("✅ Modified 'subcategory_id' to be nullable")
    except Error as e:
        print(f"⚠️  subcategory_id modification: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Schema update complete")
    
except Error as e:
    print(f"❌ Database Error: {e}")
