#!/usr/bin/env python
"""Check actual category names in database"""

from app import get_db_connection

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, name FROM categories ORDER BY name")
categories = cursor.fetchall()
cursor.close()
conn.close()

print("Actual categories in database:")
print("="*50)
for cat in categories:
    print(f"  {cat['name']}")

print(f"\nTotal: {len(categories)} categories")
