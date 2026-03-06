import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cursor = conn.cursor(dictionary=True)

# Mark all expired listings
cursor.execute("""
    UPDATE listings 
    SET status='expired' 
    WHERE expires_date < NOW() 
    AND is_sold = FALSE
    AND status = 'active'
""")
expired_count = cursor.rowcount
conn.commit()

print(f"✅ Marked {expired_count} listings as expired!")

# Show which ones were expired
cursor.execute("""
    SELECT id, title, created_at, expires_date, status 
    FROM listings 
    WHERE status = 'expired'
    LIMIT 10
""")
expired = cursor.fetchall()
print(f"\nExpired listings (now showing as 'expired' status):")
for r in expired:
    days_expired = (datetime.now() - r['expires_date']).days
    print(f"  ID {r['id']}: {r['title'][:50]}... ({days_expired} days ago)")

cursor.close()
conn.close()
