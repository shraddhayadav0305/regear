import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cur = conn.cursor()
cur.execute('SELECT DISTINCT category FROM listings')
listing_cats = [row[0] for row in cur.fetchall()]
cur.execute('SELECT slug FROM categories')
cat_slugs = [row[0] for row in cur.fetchall()]
cur.execute('SELECT name FROM categories')
cat_names = [row[0] for row in cur.fetchall()]
print('LISTING CATEGORIES NOT MATCHING CATEGORY TABLE:')
for cat in listing_cats:
    if cat not in cat_slugs and cat not in cat_names:
        print(cat)
print('\nALL LISTING CATEGORIES:')
print(listing_cats)
print('\nCATEGORY SLUGS:')
print(cat_slugs)
print('\nCATEGORY NAMES:')
print(cat_names)
cur.close()
conn.close()
