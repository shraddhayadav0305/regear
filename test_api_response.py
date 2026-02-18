import mysql.connector
import json

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
    
    # Replicate the API endpoint logic
    cursor.execute("SELECT id, name, icon FROM categories ORDER BY name")
    categories = cursor.fetchall()
    
    result = {}
    for cat in categories:
        cat_id = cat['id']
        cursor.execute(
            "SELECT id, name FROM subcategories WHERE category_id = %s ORDER BY name",
            (cat_id,)
        )
        subcats = cursor.fetchall()
        
        result[cat['name']] = {
            'icon': cat['icon'],
            'id': cat_id,
            'subcategories': [{'id': s['id'], 'name': s['name']} for s in subcats]
        }
    
    cursor.close()
    conn.close()
    
    # Print the JSON structure
    print("API RESPONSE STRUCTURE:")
    print("=" * 60)
    for key in list(result.keys())[:5]:
        print(f"\nCategory Key: '{key}'")
        print(f"  Icon: {result[key]['icon']}")
        print(f"  ID: {result[key]['id']}")
        print(f"  Subcategories: {len(result[key]['subcategories'])}")
    
    print("\n\nAll category keys:")
    for key in result.keys():
        print(f"  - '{key}'")
    
except Exception as e:
    print(f"❌ Error: {e}")
