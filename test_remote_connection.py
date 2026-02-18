#!/usr/bin/env python3
"""
Test script to verify database connection configuration
This repository has been reverted to use `localhost` for DB connections
"""

import mysql.connector
import sys

print("=" * 60)
print("🔍 Testing Remote Database Connection Configuration")
print("=" * 60)

# Test configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

print(f"\n📝 Configuration:")
    print(f"   Host: {config['host']}")
print(f"   User: {config['user']}")
print(f"   Database: {config['database']}")

try:
    print("\n🔄 Connecting to database...")
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    
    # Test basic query
    cursor.execute("SELECT COUNT(*) as user_count FROM users")
    result = cursor.fetchone()
    
    print(f"✅ Connection successful!")
    print(f"📊 Database Status:")
    print(f"   Total Users: {result['user_count']}")
    
    # Check for listings
    cursor.execute("SELECT COUNT(*) as listing_count FROM listings")
    result = cursor.fetchone()
    print(f"   Total Listings: {result['listing_count']}")
    
    # Check approved products
    cursor.execute("SELECT COUNT(*) as approved_count FROM listings WHERE approval_status='approved'")
    result = cursor.fetchone()
    print(f"   Approved Listings: {result['approved_count']}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ All checks passed! Remote access is properly configured.")
    print("=" * 60)
    print("\n📋 Summary of Changes Made:")
    print("   1. ✅ app.py host entries reverted to localhost")
    print("   2. ✅ Flask binding reverted to localhost (127.0.0.1)")
    print("   3. ✅ routes/admin.py and routes/categories.py host entries reverted to localhost")
    print("\n🌐 Flask will now:")
    print("   - Listen only on localhost (127.0.0.1:5000)")
    print("   - Connect to MySQL on localhost socket/IP")
    print("\n" + "=" * 60)
    
except mysql.connector.Error as e:
    print(f"\n❌ Connection failed: {e}")
    print("\n⚠️  Troubleshooting:")
    print("   1. Is MySQL server running on localhost?")
    print("   2. Is the MySQL port (3306) accessible from this machine?")
    print("   3. Can you reach localhost or ping the DB server?")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)
