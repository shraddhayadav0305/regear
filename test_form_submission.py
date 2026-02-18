import mysql.connector
from datetime import datetime

try:
    # Simulate form submission
    user_id = 1  # Test user
    category = "Mobiles & Accessories"
    subcategory = "Smartphones"
    title = "Test iPhone 13 Pro"
    description = "Excellent condition, minimal use"
    price = 25000
    location = "Mumbai"
    phone = "9876543210"
    email = "test@example.com"
    condition = "Like New"
    photos_str = "static/uploads/products/test1.jpg,static/uploads/products/test2.jpg"
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )
    cursor = conn.cursor()
    
    # Test the INSERT query that the backend will use
    query = """
        INSERT INTO listings (user_id, category, subcategory, title, description, price, location, phone, email, item_condition, photos, created_at, status, approval_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (user_id, category, subcategory, title, description, price, location, phone, email, condition, photos_str, datetime.now(), 'active', 'pending')
    
    cursor.execute(query, values)
    conn.commit()
    listing_id = cursor.lastrowid
    
    print(f"✅ Test INSERT successful!")
    print(f"📝 New listing ID: {listing_id}")
    print(f"   Category: {category}")
    print(f"   Subcategory: {subcategory}")
    print(f"   Title: {title}")
    print(f"   Status: pending (waiting for admin approval)")
    
    # Verify the insert
    cursor.execute("SELECT id, category, subcategory, title, status, approval_status FROM listings WHERE id=%s", (listing_id,))
    result = cursor.fetchone()
    
    if result:
        print(f"\n✅ Verification successful:")
        print(f"   ID: {result[0]}")
        print(f"   Category: {result[1]}")
        print(f"   Subcategory: {result[2]}")
        print(f"   Title: {result[3]}")
        print(f"   Status: {result[4]}")
        print(f"   Approval: {result[5]}")
    
    cursor.close()
    
    # Clean up test record
    cursor = conn.cursor()
    cursor.execute("DELETE FROM listings WHERE id=%s", (listing_id,))
    conn.commit()
    print(f"\n✅ Test record cleaned up")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error Type: {type(e)}")
