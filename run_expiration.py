import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor(dictionary=True)

# Find and expire old listings
cursor.execute('''
    SELECT id, title, expires_date FROM listings 
    WHERE is_sold=FALSE 
    AND expires_date IS NOT NULL
    AND expires_date < NOW()
    AND status != 'expired'
''')

expired_listings = cursor.fetchall()
print(f'Found {len(expired_listings)} listings to expire:')
for l in expired_listings[:10]:
    print(f"  - ID {l['id']}: {l['title']} (expired on {l['expires_date']})")

# Mark them as expired
cursor.execute('''
    UPDATE listings 
    SET status='expired' 
    WHERE is_sold=FALSE 
    AND expires_date IS NOT NULL
    AND expires_date < NOW()
''')
expired_count = cursor.rowcount
conn.commit()

print(f'\n✅ Marked {expired_count} listings as expired')

cursor.close()
conn.close()
