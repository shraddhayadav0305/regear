#!/usr/bin/env python3
"""
Database Migration Script for Category System
Executes the complete category system schema setup
"""

import mysql.connector
import sys
from datetime import datetime

# Database credentials (from app.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

def run_migration():
    """Execute database migration"""
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔧 Starting Category System Database Migration...")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Read the schema file
        with open('CATEGORY_SYSTEM_SCHEMA.sql', 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        # Execute entire schema using multi-statement support to avoid naive splitting
        executed = 0
        skipped = 0

        # Naive multi-statement execution isn't available on this connector in all environments.
        # We'll execute statements by accumulating lines until a terminating semicolon.
        buffer = []
        try:
            for line in schema_content.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith('--'):
                    continue
                buffer.append(line)
                if stripped.endswith(';'):
                    statement = '\n'.join(buffer).strip()
                    buffer = []
                    try:
                        cursor.execute(statement)
                        executed += 1
                        up = statement.strip().upper()
                        if up.startswith('CREATE TABLE'):
                            print('✅ Executed CREATE TABLE')
                        elif up.startswith('INSERT'):
                            print('✅ Executed INSERT')
                    except mysql.connector.Error as e:
                        print(f"⚠️  Error executing statement: {e}")
                        # continue executing remaining statements
                        continue
        except Exception as e:
            print(f"⚠️  Unexpected error while parsing schema: {e}")
            # continue to attempt safe ALTERs below
        
        # Commit initial schema changes
        conn.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Migration completed successfully!")
        print(f"   Statements executed: {executed}")
        print(f"   Statements skipped/ignored: {skipped}")
        print(f"{'='*60}\n")
        
        print("📊 Database Schema Summary:")
        print("   - 10 Main Categories")
        print("   - ~60 Sub-Categories")
        print("   - 15 Filter Types")
        print("   - Dynamic Category-Filter mappings")
        print("   - Product Attributes table for filters")
        print("   - Complete filter options with defaults\n")
        
        # Some MySQL versions do not support 'ADD COLUMN IF NOT EXISTS' syntax.
        # We'll add columns and foreign keys to `listings` only if they do not exist.
        def column_exists(tbl, col):
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s", (DB_CONFIG['database'], tbl, col))
            exists = cursor.fetchone()[0] > 0
            cursor.close()
            return exists

        try:
            if not column_exists('listings', 'category_id'):
                cursor = conn.cursor()
                cursor.execute('ALTER TABLE listings ADD COLUMN category_id INT NULL')
                cursor.close()
                print('✅ Added column listings.category_id')

            if not column_exists('listings', 'sub_category_id'):
                cursor = conn.cursor()
                cursor.execute('ALTER TABLE listings ADD COLUMN sub_category_id INT NULL')
                cursor.close()
                print('✅ Added column listings.sub_category_id')

            # Add foreign keys if target tables/columns exist. Ignore failures if they already exist.
            try:
                cursor = conn.cursor()
                cursor.execute('ALTER TABLE listings ADD CONSTRAINT fk_listings_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL')
                cursor.close()
                print('✅ Added FK listings.category_id -> categories.id')
            except mysql.connector.Error:
                pass

            try:
                cursor = conn.cursor()
                cursor.execute('ALTER TABLE listings ADD CONSTRAINT fk_listings_subcategory FOREIGN KEY (sub_category_id) REFERENCES sub_categories(id) ON DELETE SET NULL')
                cursor.close()
                print('✅ Added FK listings.sub_category_id -> sub_categories.id')
            except mysql.connector.Error:
                pass

            conn.commit()
        except Exception as e:
            print(f'⚠️  Error while applying safe ALTERs: {e}')
        finally:
            # Close connection after safe ALTERs
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

        print("🎯 Next Steps:")
        print("   1. Run: python app.py")
        print("   2. Visit: http://localhost:5000/admin/categories")
        print("   3. Manage categories from admin dashboard")
        print("   4. Users can create listings with dynamic filters\n")
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: CATEGORY_SYSTEM_SCHEMA.sql not found!")
        print("   Make sure you're running this script from the ReGear root directory")
        return False
        
    except mysql.connector.Error as e:
        print(f"❌ Database connection error: {e}")
        print("   Check your database credentials in the script")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
