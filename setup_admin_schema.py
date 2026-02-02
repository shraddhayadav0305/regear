#!/usr/bin/env python3
"""Fix and run the admin schema migration"""

import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

print("🔄 Running admin schema setup...\n")

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Create admin_logs table
    print("[1] Creating admin_logs table...")
    try:
        cursor.execute("""
            CREATE TABLE admin_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                admin_id INT NOT NULL,
                action VARCHAR(255),
                description TEXT,
                table_affected VARCHAR(100),
                record_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(id),
                INDEX idx_admin_id (admin_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("    ✅ admin_logs created")
    except Exception as e:
        if "already exists" in str(e):
            print("    ⊘ admin_logs already exists")
        else:
            print(f"    ⚠️  {e}")
    
    # Create complaints table
    print("[2] Creating complaints table...")
    try:
        cursor.execute("""
            CREATE TABLE complaints (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reporter_id INT,
                reported_user_id INT,
                listing_id INT,
                complaint_type VARCHAR(100),
                reason TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                admin_action TEXT,
                admin_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP NULL,
                FOREIGN KEY (reporter_id) REFERENCES users(id),
                FOREIGN KEY (reported_user_id) REFERENCES users(id),
                FOREIGN KEY (listing_id) REFERENCES listings(id),
                FOREIGN KEY (admin_id) REFERENCES users(id),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("    ✅ complaints created")
    except Exception as e:
        if "already exists" in str(e):
            print("    ⊘ complaints already exists")
        else:
            print(f"    ⚠️  {e}")
    
    # Create activity_logs table
    print("[3] Creating activity_logs table...")
    try:
        cursor.execute("""
            CREATE TABLE activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                activity_type VARCHAR(100),
                description TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("    ✅ activity_logs created")
    except Exception as e:
        if "already exists" in str(e):
            print("    ⊘ activity_logs already exists")
        else:
            print(f"    ⚠️  {e}")
    
    # Create admin_announcements table
    print("[4] Creating admin_announcements table...")
    try:
        cursor.execute("""
            CREATE TABLE admin_announcements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                admin_id INT,
                title VARCHAR(255),
                message TEXT,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("    ✅ admin_announcements created")
    except Exception as e:
        if "already exists" in str(e):
            print("    ⊘ admin_announcements already exists")
        else:
            print(f"    ⚠️  {e}")
    
    # Extend listings table
    print("[5] Extending listings table...")
    columns_to_add = [
        ("approval_status", "VARCHAR(50) DEFAULT 'pending'"),
        ("admin_notes", "TEXT"),
        ("approved_by", "INT"),
        ("approved_at", "TIMESTAMP NULL")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE listings ADD COLUMN {col_name} {col_type}")
            conn.commit()
            print(f"    ✅ Added {col_name}")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e):
                print(f"    ⊘ {col_name} already exists")
            else:
                print(f"    ⚠️  {col_name}: {e}")
    
    # Extend users table
    print("[6] Extending users table...")
    columns_to_add = [
        ("warning_count", "INT DEFAULT 0"),
        ("last_warning_at", "TIMESTAMP NULL"),
        ("suspension_reason", "TEXT")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            conn.commit()
            print(f"    ✅ Added {col_name}")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e):
                print(f"    ⊘ {col_name} already exists")
            else:
                print(f"    ⚠️  {col_name}: {e}")
    
    cursor.close()
    conn.close()
    print("\n✅ Database schema setup completed!")
    
    # Verify
    print("\n🔍 Verification...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    tables = ['admin_logs', 'complaints', 'activity_logs', 'admin_announcements']
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'regear_db'")
    existing = [t[0] for t in cursor.fetchall()]
    
    print("✅ Admin tables:")
    for table in tables:
        status = "✅" if table in existing else "❌"
        print(f"   {status} {table}")
    
    cursor.execute("SHOW COLUMNS FROM listings")
    cols = [c[0] for c in cursor.fetchall()]
    print("✅ Listings columns:")
    for col in ['approval_status', 'admin_notes', 'approved_by', 'approved_at']:
        status = "✅" if col in cols else "❌"
        print(f"   {status} {col}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
