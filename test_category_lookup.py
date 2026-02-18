import mysql.connector
from urllib.parse import quote, unquote

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )

# Get all category names from DB
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, name FROM categories ORDER BY name")
categories = cursor.fetchall()
cursor.close()
conn.close()

print("Testing category lookup simulation:")
print("=" * 70)

for cat in categories:
    cat_name = cat['name']
    # Simulate what JavaScript sends - encoded then decoded by Flask
    encoded = quote(cat_name)
    decoded = unquote(encoded)
    
    print(f"\nCategory: '{cat_name}'")
    print(f"  Encoded: {encoded}")
    print(f"  Decoded: {decoded}")
    print(f"  Match: {'✅' if decoded == cat_name else '❌'}")
    
    # Simulate database lookup
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM categories WHERE name = %s", (decoded,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        print(f"  Database lookup: ✅ Found (ID: {result['id']})")
    else:
        print(f"  Database lookup: ❌ NOT FOUND")
