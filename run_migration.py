#!/usr/bin/env python3
"""Run the fixed SQL migration"""

import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

print("🔄 Running fixed SQL migration...\n")

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Read SQL file
    with open('ADMIN_SCHEMA_FIXED.sql', 'r') as f:
        sql_content = f.read()
    
    # Execute each statement
    statements = sql_content.split(';')
    for i, stmt in enumerate(statements, 1):
        stmt = stmt.strip()
        if stmt and not stmt.startswith('--'):
            try:
                print(f"[{i}] Executing: {stmt[:70]}...")
                cursor.execute(stmt)
                conn.commit()
                print(f"    ✅ Done")
            except mysql.connector.Error as e:
                if "already exists" in str(e) or "Duplicate" in str(e):
                    print(f"    ⊘ Already exists")
                else:
                    print(f"    ❌ Error: {e}")
    
    cursor.close()
    conn.close()
    print("\n✅ Migration completed!")
    
    # Verify tables
    print("\n🔍 Verifying tables...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SHOW TABLES LIKE '%admin%' OR SHOW TABLES LIKE '%complaint%'")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'regear_db' AND TABLE_NAME IN ('admin_logs', 'complaints', 'activity_logs', 'admin_announcements')")
    
    tables = cursor.fetchall()
    if tables:
        print("✅ Admin tables found:")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("❌ No admin tables found")
    
    # Check columns on listings and users
    print("\n🔍 Verifying extended columns...")
    cursor.execute("SHOW COLUMNS FROM listings LIKE 'approval_status'")
    if cursor.fetchone():
        print("✅ listings.approval_status found")
    else:
        print("❌ listings.approval_status NOT found")
    
    cursor.execute("SHOW COLUMNS FROM users LIKE 'warning_count'")
    if cursor.fetchone():
        print("✅ users.warning_count found")
    else:
        print("❌ users.warning_count NOT found")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
