#!/usr/bin/env python3
"""Delete test listings created during debugging.

Run this script to remove any listings that were created as part of the debug/SQLAlchemy tests,
so they no longer show up in the admin products panel or user listings.

Usage:
    python delete_test_ad.py

This script targets listings whose title contains the string "Test Ad from SQLAlchemy".
"""

import mysql.connector

TARGET_TITLE = "Test Ad from SQLAlchemy"

if __name__ == "__main__":
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, user_id, approval_status FROM listings WHERE title = %s",
        (TARGET_TITLE,)
    )
    rows = cursor.fetchall()

    if not rows:
        print(f"No listings found with title '{TARGET_TITLE}'")
    else:
        print(f"Found {len(rows)} listing(s) to delete:")
        for row in rows:
            print(f"  - id={row[0]}, user_id={row[2]}, status={row[3]}")

        confirm = input("Delete these listings? (y/N): ")
        if confirm.strip().lower() == 'y':
            cursor.execute("DELETE FROM listings WHERE title = %s", (TARGET_TITLE,))
            conn.commit()
            print(f"Deleted {cursor.rowcount} listing(s)")
        else:
            print("Aborted. No changes made.")

    cursor.close()
    conn.close()
