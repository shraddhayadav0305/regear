import mysql.connector

conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT id, title, category, status, approval_status, created_at FROM listings ORDER BY created_at DESC')
for row in cursor.fetchall():
    print(f"ID:{row['id']} Title:{row['title']} Category:{row['category']} Status:{row['status']} Approval:{row['approval_status']} Created:{row['created_at']}")
conn.close()
