#!/usr/bin/env python3
"""
Test script to verify the homepage featured listings feature
"""

import mysql.connector
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )

def test_database():
    """Test database connection and check listings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if listings table exists
        cursor.execute("DESC listings")
        print("✓ Listings table exists")
        
        # Check total listings
        cursor.execute("SELECT COUNT(*) as count FROM listings")
        total = cursor.fetchone()['count']
        print(f"✓ Total listings in database: {total}")
        
        # Check approved listings
        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE approval_status='approved'")
        approved = cursor.fetchone()['count']
        print(f"✓ Approved listings: {approved}")
        
        # Check pending listings
        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE approval_status='pending'")
        pending = cursor.fetchone()['count']
        print(f"✓ Pending listings: {pending}")
        
        # Check for sample approved listings
        cursor.execute("""
            SELECT id, title, category, approval_status, created_at 
            FROM listings 
            WHERE approval_status='approved' 
            LIMIT 5
        """)
        listings = cursor.fetchall()
        
        if listings:
            print(f"\n✓ Found {len(listings)} approved listings:")
            for listing in listings:
                print(f"  - ID: {listing['id']}, Title: {listing['title']}, Category: {listing['category']}")
        else:
            print("\n⚠ No approved listings found in database")
            print("\nYou need to:")
            print("1. Create a user account")
            print("2. Post an ad")
            print("3. Login to admin panel and approve it")
            print("4. Then the homepage will show featured listings")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Homepage Featured Listings Feature")
    print("=" * 60)
    test_database()
    print("\n" + "=" * 60)
    print("Test complete! Visit http://localhost:5000 to see results")
    print("=" * 60)
