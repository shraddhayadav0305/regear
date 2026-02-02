#!/usr/bin/env python3
"""Check database tables and create missing ones"""

import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

print("🔍 Checking database tables...\n")

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    
    print(f"📊 Total tables: {len(tables)}\n")
    print("Tables found:")
    for table in sorted(tables):
        print(f"  - {table}")
    
    # Check if listings exists
    if 'listings' not in tables:
        print("\n⚠️  listings table NOT found!")
        print("Creating listings table...")
        
        cursor.execute("""
            CREATE TABLE listings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                category VARCHAR(100),
                subcategory VARCHAR(100),
                title VARCHAR(200),
                description TEXT,
                price DECIMAL(10, 2),
                location VARCHAR(200),
                phone VARCHAR(20),
                email VARCHAR(150),
                condition VARCHAR(50),
                photos LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approval_status VARCHAR(50) DEFAULT 'pending',
                admin_notes TEXT,
                approved_by INT,
                approved_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                INDEX idx_user_id (user_id),
                INDEX idx_approval_status (approval_status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("✅ listings table created\n")
    else:
        print("\n✅ listings table exists")
    
    # Check if users exists and has required columns
    if 'users' in tables:
        cursor.execute("SHOW COLUMNS FROM users")
        cols = [c[0] for c in cursor.fetchall()]
        print(f"✅ users table has {len(cols)} columns")
        
        required_cols = ['warning_count', 'last_warning_at', 'suspension_reason']
        for col in required_cols:
            if col in cols:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} missing")
    
    # Now create complaints table without listings FK if needed
    print("\nCreating complaints table...")
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
                FOREIGN KEY (admin_id) REFERENCES users(id),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("✅ complaints table created")
    except Exception as e:
        if "already exists" in str(e):
            print("⊘ complaints table already exists")
        else:
            print(f"⚠️  {e}")
    
    cursor.close()
    conn.close()
    print("\n✅ Database check complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
