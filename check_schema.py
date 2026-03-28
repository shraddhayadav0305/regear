import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shra@0303",
    database="regear_db"
)

cursor = conn.cursor()
cursor.execute("DESCRIBE listings")
columns = cursor.fetchall()

print("Current listings table columns:")
for col in columns:
    print(f"  {col[0]}: {col[1]}")

cursor.close()
conn.close()
