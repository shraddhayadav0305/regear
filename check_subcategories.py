import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor(dictionary=True)

# Check sub_categories table
print('sub_categories table:')
cursor.execute('SELECT COUNT(*) as count FROM sub_categories')
result = cursor.fetchone()
print(f'  Total records: {result["count"]}')

# Check subcategories table
print('\nsubcategories table:')
cursor.execute('SELECT COUNT(*) as count FROM subcategories')
result = cursor.fetchone()
print(f'  Total records: {result["count"]}')

# Check categories table
print('\ncategories table:')
cursor.execute('SELECT id, name FROM categories LIMIT 3')
categories = cursor.fetchall()
for cat in categories:
    print(f'  - {cat["name"]} (ID: {cat["id"]})')
    
    # Check subcategories for this category in both tables
    cursor.execute('SELECT COUNT(*) as count FROM sub_categories WHERE category_id = %s', (cat['id'],))
    sub_result = cursor.fetchone()
    print(f'      sub_categories: {sub_result["count"]} records')
    
    cursor.execute('SELECT COUNT(*) as count FROM subcategories WHERE category_id = %s', (cat['id'],))
    sub_result = cursor.fetchone()
    print(f'      subcategories: {sub_result["count"]} records')

cursor.close()
conn.close()
