import mysql.connector
from app import verify_password

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Shra@0303',
        database='regear_db'
    )
    cursor = conn.cursor(dictionary=True)

    # Check admin user with password
    cursor.execute('SELECT id, username, email, role, password FROM users WHERE email="admin@regear.com"')
    admin_user = cursor.fetchone()

    if admin_user:
        print(f'✅ Admin user found:')
        print(f'  ID: {admin_user["id"]}')
        print(f'  Username: {admin_user["username"]}')
        print(f'  Email: {admin_user["email"]}')
        print(f'  Role: {admin_user["role"]}')
        print(f'  Password hash: {admin_user["password"][:20]}...')

        # Test password verification
        is_correct = verify_password(admin_user['password'], 'admin123')
        print(f'  Password "admin123" correct: {is_correct}')

    else:
        print('❌ Admin user NOT found!')

    cursor.close()
    conn.close()

except Exception as e:
    print(f'❌ Database error: {e}')
    import traceback
    traceback.print_exc()