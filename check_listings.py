import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )
    cursor = conn.cursor()
    
    # Check if listings table exists and show its structure
    cursor.execute("DESCRIBE listings")
    columns = cursor.fetchall()
    
    print("📋 LISTINGS TABLE STRUCTURE:")
    print("-" * 80)
    print(f"{'Column Name':<20} {'Type':<30} {'Null':<5} {'Key':<10} {'Default':<15} {'Extra':<15}")
    print("-" * 80)
    for col in columns:
        col_name, col_type, is_null, key, default, extra = col
        print(f"  {col_name:<19} {str(col_type):<29} {str(is_null):<4} {str(key):<9} {str(default):<14} {str(extra):<14}")
    
    cursor.close()
    conn.close()
    print("\n✅ Connection successful")
except Error as e:
    print(f"❌ Error: {e}")
