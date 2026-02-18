#!/usr/bin/env python3
"""Add admin approval columns to `listings` table if they are missing."""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

COLS = {
    'approval_status': "VARCHAR(50) DEFAULT 'pending'",
    'admin_notes': 'TEXT',
    'approved_by': 'INT',
    'approved_at': 'TIMESTAMP NULL'
}

def column_exists(cursor, table, column):
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE table_schema=%s AND table_name=%s AND column_name=%s
    """, (DB_CONFIG['database'], table, column))
    return cursor.fetchone()[0] > 0

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        for col, col_def in COLS.items():
            if not column_exists(cursor, 'listings', col):
                sql = f"ALTER TABLE listings ADD COLUMN {col} {col_def};"
                print(f"Adding column: {col} -> {col_def}")
                cursor.execute(sql)
                conn.commit()
            else:
                print(f"Column exists: {col}")
    finally:
        cursor.close()
        conn.close()

    print("Done.")

if __name__ == '__main__':
    main()
