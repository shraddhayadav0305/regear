import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get categories
    cursor.execute("SELECT id, name, icon FROM categories ORDER BY id LIMIT 10")
    categories = cursor.fetchall()
    
    print("CATEGORIES IN DATABASE:")
    print("=" * 60)
    for cat in categories:
        print(f"ID: {cat['id']}, Name: '{cat['name']}', Icon: {cat['icon']}")
        
        # Get subcategories for each
        cursor.execute(
            "SELECT id, name FROM subcategories WHERE category_id = %s ORDER BY id",
            (cat['id'],)
        )
        subcats = cursor.fetchall()
        print(f"  Subcategories ({len(subcats)}):")
        for sub in subcats:
            print(f"    - {sub['name']}")
        print()
    
    cursor.close()
    conn.close()
    print("✅ Done")
except Exception as e:
    print(f"❌ Error: {e}")
