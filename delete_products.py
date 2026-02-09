import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Shra@0303',
        database='regear_db'
    )
    cursor = conn.cursor()
    
    # Delete all listings
    cursor.execute("DELETE FROM listings")
    conn.commit()
    
    # Get count to verify
    cursor.execute("SELECT COUNT(*) as cnt FROM listings")
    result = cursor.fetchone()
    print(f'✅ All products deleted successfully!')
    print(f'Remaining listings: {result[0]}')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ Error: {e}')
