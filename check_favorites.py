import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shra@0303",
    database="regear_db"
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES LIKE 'favorites'")
result = cursor.fetchall()
print('favorites table exists:', len(result) > 0)

cursor.close()
conn.close()