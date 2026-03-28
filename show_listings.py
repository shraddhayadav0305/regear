import mysql.connector

conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT COUNT(*) as cnt FROM listings')
print('Total listings:', cursor.fetchone()['cnt'])
cursor.execute('SELECT id, title, category, status, approval_status FROM listings')
for row in cursor.fetchall():
    print(f"ID:{row['id']} Title:{row['title']} Category:{row['category']} Status:{row['status']} Approval:{row['approval_status']}")
conn.close()
