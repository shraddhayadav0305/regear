#!/usr/bin/env python3
"""Create listings table and complaints table properly"""

import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

print("🔄 Setting up database tables...\n")

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check if listings exists, if not create it
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
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
            item_condition VARCHAR(50),
            photos LONGTEXT,
            status VARCHAR(50) DEFAULT 'active',
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
    print("✅ listings table ready")
    
    # Create product_images table to store individual image paths
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                listing_id INT NOT NULL,
                image_path VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
                INDEX idx_listing_id (listing_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        print("✅ product_images table ready")
    except Exception as e:
        if "already exists" in str(e):
            print("⊘ product_images table already exists")
        else:
            raise
    
    # Check if products exists (alias for listings)
    cursor.execute("SELECT COUNT(*) FROM information_schema.TABLES WHERE table_name='products' AND table_schema='regear_db'")
    if cursor.fetchone()[0] > 0:
        print("✅ products table exists (legacy)")
    
    # Create complaints table
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
        print("✅ complaints table created")
    except Exception as e:
        if "already exists" in str(e):
            print("⊘ complaints table already exists")
        else:
            raise
    
    cursor.close()
    conn.close()
    print("\n✅ All tables ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

