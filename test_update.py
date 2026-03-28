import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )

# Mimic view_listing
listing_id = 6
try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Increment view count
    print("Executing UPDATE...")
    cursor.execute("UPDATE listings SET view_count = view_count + 1 WHERE id = %s", (listing_id,))
    conn.commit()
    print("Committed")
    
    cursor.execute("SELECT view_count FROM listings WHERE id = %s", (listing_id,))
    result = cursor.fetchone()
    print("View count after update:", result['view_count'])
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print("Error:", e)