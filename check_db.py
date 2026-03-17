#!/usr/bin/env python3
"""
Simple database check to verify ad posting
"""

import mysql.connector
from datetime import datetime

def check_database():
    """Check if ads are being saved to database"""
    print("🔍 Checking database for saved ads...")

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shra@0303",
            database="regear_db"
        )
        cursor = conn.cursor(dictionary=True)

        # Check total listings
        cursor.execute("SELECT COUNT(*) as total FROM listings")
        result = cursor.fetchone()
        total_listings = result['total']
        print(f"   Total listings in database: {total_listings}")

        # Check recent listings (last 10)
        cursor.execute("""
            SELECT id, user_id, title, category, subcategory, price, status, approval_status, created_at
            FROM listings
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent_listings = cursor.fetchall()

        print(f"\n   Recent {len(recent_listings)} listings:")
        for listing in recent_listings:
            print(f"   - ID {listing['id']}: '{listing['title']}' by user {listing['user_id']} ({listing['approval_status']})")

        # Check if test ad exists
        cursor.execute("SELECT * FROM listings WHERE title LIKE '%Test iPhone%' ORDER BY created_at DESC LIMIT 1")
        test_ad = cursor.fetchone()
        if test_ad:
            print(f"\n   ✅ Test ad found: ID {test_ad['id']}, Title: '{test_ad['title']}', Status: {test_ad['approval_status']}")
            return True
        else:
            print("\n   ❌ Test ad not found in database")
            return False

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

if __name__ == "__main__":
    check_database()