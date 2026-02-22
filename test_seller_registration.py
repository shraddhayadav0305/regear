import mysql.connector
from datetime import datetime

# simple test script to verify that seller registration
data writes package and fee correctly

try:
    # test data
    test_username = "pkg_seller"
    test_email = "pkg_seller@test.com"
    test_password = "password123"  # we'll store plaintext for test
    test_phone = "9999999999"
    test_role = "seller"
    test_package = "15"
    fee_map = {"10": 199.00, "15": 349.00, "20": 499.00}
    test_fee = fee_map[test_package]

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )
    cursor = conn.cursor()

    # perform insert similar to registration logic
    cursor.execute("DELETE FROM users WHERE email=%s", (test_email,))
    conn.commit()

    cursor.execute(
        "INSERT INTO users (role, username, email, password, phone, created_at, seller_package, registration_fee)"
        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (test_role, test_username, test_email, test_password, test_phone, datetime.now(), test_package, test_fee)
    )
    conn.commit()
    user_id = cursor.lastrowid
    print(f"✅ Inserted test seller user id={user_id}")

    cursor.execute(
        "SELECT role, seller_package, registration_fee FROM users WHERE id=%s", (user_id,)
    )
    row = cursor.fetchone()
    if row:
        print(f"👀 Retrieved: role={row[0]}, package={row[1]}, fee={row[2]}")
        assert row[0] == test_role
        assert row[1] == test_package
        assert float(row[2]) == test_fee
        print("✅ Verification passed")
    else:
        print("❌ Could not verify inserted user")

    # clean up
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    print("✅ Cleaned up test record")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error during test: {e}")
