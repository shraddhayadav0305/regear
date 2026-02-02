import mysql.connector
import hashlib

# Test the database directly
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shra@0303",
    database="regear_db"
)

cursor = conn.cursor()

print("Checking test users...")
cursor.execute("SELECT id, username, email, role FROM users WHERE email LIKE '%test%' OR email LIKE '%admin%'")
users = cursor.fetchall()

for user in users:
    print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}")

print("\n✅ Database connection works!")
cursor.close()
conn.close()
