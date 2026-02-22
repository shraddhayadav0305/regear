import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )

# simple check that conversation and messages tables exist and can be inserted into
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'conversations'")
    if cursor.fetchone():
        print("✅ conversations table exists")
    else:
        print("❌ conversations table missing")

    cursor.execute("SHOW TABLES LIKE 'messages'")
    if cursor.fetchone():
        print("✅ messages table exists")
    else:
        print("❌ messages table missing")

    cursor.execute("SHOW TABLES LIKE 'notifications'")
    if cursor.fetchone():
        print("✅ notifications table exists")
    else:
        print("⚠ notifications table missing (optional)")

    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error checking chat tables: {e}")
