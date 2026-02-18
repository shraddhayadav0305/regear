import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor(dictionary=True)

print('Categories and their subcategories count:')
cursor.execute('SELECT id, name FROM categories ORDER BY id')
categories = cursor.fetchall()

sub_count_total = 0
subcategories_count_total = 0

for cat in categories:
    cursor.execute('SELECT COUNT(*) as count FROM sub_categories WHERE category_id = %s', (cat['id'],))
    sub_result = cursor.fetchone()
    sub_count = sub_result["count"]
    sub_count_total += sub_count
    
    cursor.execute('SELECT COUNT(*) as count FROM subcategories WHERE category_id = %s', (cat['id'],))
    subcat_result = cursor.fetchone()
    subcat_count = subcat_result["count"]
    subcategories_count_total += subcat_count
    
    print(f'  {cat["name"]}: sub_categories={sub_count}, subcategories={subcat_count}')

print(f'\nTotals: sub_categories={sub_count_total}, subcategories={subcategories_count_total}')

# Check a sample from each table
print('\nSample from sub_categories:')
cursor.execute('SELECT id, name, category_id FROM sub_categories LIMIT 5')
rows = cursor.fetchall()
for row in rows:
    print(f'  {row}')

print('\nSample from subcategories:')
cursor.execute('SELECT id, name, category_id FROM subcategories LIMIT 5')
rows = cursor.fetchall()
for row in rows:
    print(f'  {row}')

cursor.close()
conn.close()
