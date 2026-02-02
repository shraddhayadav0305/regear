#!/usr/bin/env python3
"""
Test Admin Login & Role-Based Access Setup Script
Creates test users and runs database migrations
"""

import mysql.connector
import hashlib
import secrets
import sys

# Database credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${password_hash}"

def run_migration():
    """Run ADMIN_SCHEMA.sql migration"""
    print("🔄 Running database migration...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Read and execute migration
        with open('ADMIN_SCHEMA.sql', 'r') as f:
            migration_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = migration_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as e:
                    # Ignore "table already exists" errors
                    if "already exists" not in str(e):
                        print(f"⚠️  Warning: {e}")
        
        conn.commit()
        print("✅ Database migration completed!")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_test_users():
    """Create test admin and regular users"""
    print("\n📝 Creating test users...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test users to create
        test_users = [
            {
                'role': 'admin',
                'username': 'admin',
                'email': 'admin@regear.com',
                'password': 'admin123',
                'phone': '9999999999'
            },
            {
                'role': 'buyer',
                'username': 'testbuyer',
                'email': 'buyer@test.com',
                'password': 'buyer123',
                'phone': '8888888888'
            },
            {
                'role': 'seller',
                'username': 'testseller',
                'email': 'seller@test.com',
                'password': 'seller123',
                'phone': '7777777777'
            },
            {
                'role': 'blocked',
                'username': 'blockeduser',
                'email': 'blocked@test.com',
                'password': 'blocked123',
                'phone': '6666666666'
            }
        ]
        
        for user in test_users:
            hashed_pw = hash_password(user['password'])
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email=%s", (user['email'],))
            if cursor.fetchone():
                print(f"⊘ {user['username']} already exists, skipping...")
                continue
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (role, username, email, password, phone, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (user['role'], user['username'], user['email'], hashed_pw, user['phone']))
            
            conn.commit()
            print(f"✅ Created {user['role']:8} user: {user['username']:15} ({user['email']})")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return False

def verify_tables():
    """Verify admin tables were created"""
    print("\n🔍 Verifying database tables...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        tables_to_check = [
            'admin_logs',
            'complaints',
            'activity_logs',
            'admin_announcements'
        ]
        
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        all_found = True
        for table in tables_to_check:
            if table in existing_tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' NOT FOUND")
                all_found = False
        
        cursor.close()
        conn.close()
        return all_found
    except Exception as e:
        print(f"❌ Table verification failed: {e}")
        return False

def verify_admin_user():
    """Verify admin user was created"""
    print("\n👤 Verifying admin user...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, email, role FROM users WHERE role='admin' LIMIT 1")
        admin = cursor.fetchone()
        
        if admin:
            print(f"✅ Admin user found:")
            print(f"   ID: {admin['id']}")
            print(f"   Username: {admin['username']}")
            print(f"   Email: {admin['email']}")
            print(f"   Role: {admin['role']}")
        else:
            print("❌ No admin user found!")
        
        cursor.close()
        conn.close()
        return admin is not None
    except Exception as e:
        print(f"❌ Admin verification failed: {e}")
        return False

def print_test_credentials():
    """Print test credentials for manual testing"""
    print("\n" + "="*60)
    print("🧪 TEST CREDENTIALS FOR MANUAL TESTING")
    print("="*60)
    
    credentials = [
        ("Admin User", "admin", "admin@regear.com", "admin123"),
        ("Buyer User", "testbuyer", "buyer@test.com", "buyer123"),
        ("Seller User", "testseller", "seller@test.com", "seller123"),
        ("Blocked User", "blockeduser", "blocked@test.com", "blocked123"),
    ]
    
    for desc, username, email, password in credentials:
        print(f"\n{desc}:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Username: {username}")
    
    print("\n" + "="*60)
    print("📝 TESTING STEPS:")
    print("="*60)
    print("1. Start Flask: python app.py")
    print("2. Go to: http://localhost:5000/login")
    print("3. Try each user above")
    print("4. Test access to: http://localhost:5000/admin/dashboard")
    print("   - Admin should see dashboard ✅")
    print("   - Others should be redirected ❌")
    print("="*60 + "\n")

def main():
    print("🚀 ReGear Admin Test Setup\n")
    
    # Step 1: Run migration
    if not run_migration():
        print("⚠️  Migration had issues, continuing...")
    
    # Step 2: Verify tables
    if not verify_tables():
        print("⚠️  Some tables may be missing")
    
    # Step 3: Create test users
    if not create_test_users():
        print("❌ Failed to create test users")
        sys.exit(1)
    
    # Step 4: Verify admin user
    if not verify_admin_user():
        print("❌ Admin user verification failed")
        sys.exit(1)
    
    # Step 5: Print credentials
    print_test_credentials()
    
    print("✅ Setup complete! Ready for testing.\n")

if __name__ == "__main__":
    main()
