#!/usr/bin/env python3
"""Add missing boost columns to listings table for OLX-style boost feature."""

import mysql.connector
from mysql.connector import Error

def add_boost_columns():
    """Add or update boost-related columns in listings table."""
    conn = None
    cursor = None
    
    try:
        print("Connecting to database...")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shra@0303",
            database="regear_db"
        )
        
        cursor = conn.cursor()
        
        # List of columns to add/update
        columns_to_add = [
            ("is_featured", "TINYINT(1) DEFAULT 0"),
            ("is_urgent", "TINYINT(1) DEFAULT 0"),
            ("boost_priority", "INT DEFAULT 0"),
        ]
        
        print("\nChecking and adding columns to listings table...")
        
        # Get existing columns
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='listings' AND TABLE_SCHEMA='regear_db'")
        existing_cols = {row[0] for row in cursor.fetchall()}
        
        for col_name, col_definition in columns_to_add:
            if col_name not in existing_cols:
                print(f"  ✓ Adding column: {col_name}")
                try:
                    cursor.execute(f"ALTER TABLE listings ADD COLUMN {col_name} {col_definition}")
                    conn.commit()
                    print(f"    SUCCESS: {col_name} added")
                except Error as e:
                    print(f"    ERROR: {e}")
                    conn.rollback()
            else:
                print(f"  ✓ Column already exists: {col_name}")
        
        # Verify boost_expires_date column
        if "boost_expires_date" in existing_cols:
            print(f"  ✓ Column already exists: boost_expires_date")
        else:
            print(f"  ✓ Adding column: boost_expires_date")
            try:
                cursor.execute("ALTER TABLE listings ADD COLUMN boost_expires_date TIMESTAMP NULL DEFAULT NULL")
                conn.commit()
                print(f"    SUCCESS: boost_expires_date added")
            except Error as e:
                print(f"    ERROR: {e}")
                conn.rollback()
        
        # Verify boost_type column
        if "boost_type" in existing_cols:
            print(f"  ✓ Column already exists: boost_type")
        else:
            print(f"  ✓ Adding column: boost_type")
            try:
                cursor.execute("ALTER TABLE listings ADD COLUMN boost_type VARCHAR(50) DEFAULT NULL")
                conn.commit()
                print(f"    SUCCESS: boost_type added")
            except Error as e:
                print(f"    ERROR: {e}")
                conn.rollback()
        
        print("\n✅ Database migration complete!")
        
        # Show final schema
        print("\nFinal columns related to boost:")
        cursor.execute("SELECT COLUMN_NAME, COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='listings' AND TABLE_SCHEMA='regear_db' AND (COLUMN_NAME LIKE 'boost_%' OR COLUMN_NAME LIKE 'is_%')")
        for col_name, col_type in cursor.fetchall():
            print(f"  {col_name}: {col_type}")
        
    except Error as e:
        print(f"❌ Error: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    add_boost_columns()
