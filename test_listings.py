from app import get_db_connection

def test_listings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        user_id = 1  # Replace with the actual user ID to test
        cursor.execute("SELECT id, title, category, subcategory, price, status, approval_status, created_at, photos FROM listings WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
        listings = cursor.fetchall()
        cursor.close()
        conn.close()
        print("Listings for user_id=1:", listings)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_listings()