import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cur = conn.cursor(dictionary=True)
cur.execute('SELECT category, status, approval_status, COUNT(*) AS cnt FROM listings GROUP BY category, status, approval_status ORDER BY category, status, approval_status')
rows = cur.fetchall()
print('CATEGORY STATUS COUNTS:')
for row in rows:
    print(row)
cur.close()
conn.close()
