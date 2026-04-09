import mysql.connector

conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cur = conn.cursor(dictionary=True)
cur.execute('SELECT id, name, slug FROM categories ORDER BY id')
print('CATEGORIES:')
for row in cur.fetchall():
    print(row)
print('\nLISTING CATEGORY COUNTS:')
cur.execute('SELECT category, COUNT(*) AS cnt FROM listings GROUP BY category ORDER BY cnt DESC')
for row in cur.fetchall():
    print(row)
print('\nSAMPLE LISTINGS:')
cur.execute('SELECT id, title, category, subcategory, status, approval_status FROM listings WHERE category IS NOT NULL ORDER BY id DESC LIMIT 50')
for row in cur.fetchall():
    print(row)
cur.close()
conn.close()
