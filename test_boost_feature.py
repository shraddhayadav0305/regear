#!/usr/bin/env python3
"""Test script to verify boost feature is working correctly."""

import sys
import mysql.connector
from datetime import datetime, timedelta

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shra@0303",
    database="regear_db"
)

cursor = conn.cursor(dictionary=True)

print("=" * 60)
print("BOOST FEATURE TEST")
print("=" * 60)

# Test 1: Check if boost columns exist
print("\n✓ Test 1: Verifying boost columns exist...")
cursor.execute("DESCRIBE listings WHERE Field IN ('boost_type', 'boost_expires_date')")
columns = cursor.fetchall()
print(f"  Found {len(columns)} boost-related columns")

# Test 2: Get a sample listing and check boost calculation
print("\n✓ Test 2: Checking is_boosted calculation query...")
cursor.execute("""
    SELECT 
        l.id,
        l.title,
        l.boost_type,
        l.boost_expires_date,
        CASE WHEN l.boost_expires_date > NOW() THEN 1 ELSE 0 END AS is_boosted
    FROM listings l
    WHERE l.user_id = 2
    LIMIT 1
""")

listing = cursor.fetchone()
if listing:
    print(f"  Sample Listing ID: {listing['id']}")
    print(f"  Title: {listing['title']}")
    print(f"  Boost Type: {listing['boost_type']}")
    print(f"  Boost Expires: {listing['boost_expires_date']}")
    print(f"  Is Boosted (calculated): {listing['is_boosted']}")
else:
    print("  No listings found for user 2")

# Test 3: Check if boost_packages table exists (if needed)
print("\n✓ Test 3: Checking boost packages setup...")
cursor.execute("""
    SELECT * FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = 'regear_db' 
    AND TABLE_NAME = 'boost_packages'
""")
if cursor.fetchone():
    print("  boost_packages table exists ✓")
    cursor.execute("SELECT COUNT(*) as count FROM boost_packages")
    count = cursor.fetchone()
    print(f"  Total packages: {count['count']}")
else:
    print("  boost_packages table does NOT exist (OK - using hardcoded packages)")

# Test 4: Check ad_boosts table
print("\n✓ Test 4: Checking ad_boosts table...")
cursor.execute("""
    SELECT * FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = 'regear_db' 
    AND TABLE_NAME = 'ad_boosts'
""")
if cursor.fetchone():
    print("  ad_boosts table exists ✓")
    cursor.execute("SELECT COUNT(*) as count FROM ad_boosts WHERE status = 'active'")
    count = cursor.fetchone()
    print(f"  Total active boosts: {count['count']}")
else:
    print("  ad_boosts table does NOT exist - need to create it!")

# Test 5: Check boosted_listings table
print("\n✓ Test 5: Checking boosted_listings table...")
cursor.execute("""
    SELECT * FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = 'regear_db' 
    AND TABLE_NAME = 'boosted_listings'
""")
if cursor.fetchone():
    print("  boosted_listings table exists ✓")
    cursor.execute("SELECT COUNT(*) as count FROM boosted_listings WHERE status = 'active'")
    count = cursor.fetchone()
    print(f"  Total featured boosts: {count['count']}")
else:
    print("  boosted_listings table does NOT exist - need to create it!")

# Test 6: Simulate boost application
print("\n✓ Test 6: Simulating boost application...")
print("  (This is a DRY RUN - no changes to database)")

test_listing_id = 1
test_user_id = 2
test_boost_type = "standard"
test_days = 7
boost_until = datetime.now() + timedelta(days=test_days)

print(f"  Would boost listing {test_listing_id}")
print(f"  Boost type: {test_boost_type}")
print(f"  Boost duration: {test_days} days")
print(f"  Boost expires: {boost_until.strftime('%d %b %Y %H:%M:%S')}")

# Test 7: Check SQL sorting query
print("\n✓ Test 7: Testing sort query with boosted priority...")
cursor.execute("""
    SELECT 
        l.id,
        l.title,
        l.price,
        l.boost_type,
        CASE WHEN l.boost_expires_date > NOW() THEN 1 ELSE 0 END AS is_boosted
    FROM listings l
    WHERE l.user_id = 2
    ORDER BY is_boosted DESC, l.created_at DESC
    LIMIT 3
""")
listings = cursor.fetchall()
if listings:
    print(f"  Found {len(listings)} listings:")
    for idx, listing in enumerate(listings, 1):
        boosted_status = "🔥 BOOSTED" if listing['is_boosted'] else "  Active"
        print(f"    {idx}. {boosted_status} - {listing['title'][:40]}")
else:
    print("  No listings found")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

cursor.close()
conn.close()
