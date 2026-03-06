import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cursor = conn.cursor(dictionary=True)

# Check current listings
cursor.execute('SELECT id, title, created_at, expires_date, status FROM listings LIMIT 5;')
result = cursor.fetchall()
print('Sample listings:')
for r in result:
    print(f"  ID {r['id']}: {r['title'][:30]}...")
    print(f"      Created: {r['created_at']}, Expires: {r['expires_date']}")

# Set expires_date to 5 days from created_at for all listings
cursor.execute("""
    UPDATE listings 
    SET expires_date = DATE_ADD(created_at, INTERVAL 5 DAY)
    WHERE expires_date IS NULL
""")
updated = cursor.rowcount
conn.commit()
print(f"\n✅ Set expires_date for {updated} listings")

# Now check which listings have expired (past 5 days)
cursor.execute("""
    SELECT id, title, created_at, expires_date 
    FROM listings 
    WHERE expires_date < NOW() 
    AND is_sold = FALSE
    AND status != 'expired'
    LIMIT 5
""")
expired = cursor.fetchall()
print(f"\nListings that have expired (past their 5-day trial):")
for r in expired:
    days_expired = (datetime.now() - r['expires_date']).days
    print(f"  ID {r['id']}: {r['title'][:40]}... (expired {days_expired} days ago)")

cursor.close()
conn.close()
