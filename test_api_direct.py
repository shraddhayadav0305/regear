import mysql.connector
import json

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor(dictionary=True)

# Test the same logic as the /api/categories endpoint
print("Testing /api/categories endpoint logic...")

cursor.execute("SELECT id, name, icon FROM categories ORDER BY name")
categories = cursor.fetchall()

result = {}
for cat in categories:
    cat_id = cat['id']
    # Fetch subcategories for this category
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

# Display the result
print(f"\nTotal categories: {len(result)}")
print("\nFirst 3 categories with subcategories count:")
for i, (cat_name, cat_data) in enumerate(list(result.items())[:3]):
    print(f"\n{i+1}. {cat_name}")
    print(f"   Icon: {cat_data.get('icon', 'N/A')}")
    print(f"   ID: {cat_data.get('id', 'N/A')}")
    print(f"   Subcategories: {len(cat_data.get('subcategories', []))}")
    
    if cat_data.get('subcategories'):
        print("   Subcategories list:")
        for sub in cat_data['subcategories']:
            print(f"      - {sub['name']}")

# Show summary
print("\n\nSummary of all categories:")
for cat_name, cat_data in result.items():
    sub_count = len(cat_data.get('subcategories', []))
    print(f"  {cat_name}: {sub_count} subcategories")
