import mysql.connector
import sys

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303"
    )
    cursor = conn.cursor()
    
    print("🔧 Configuring MySQL for remote access...")
    
    # Allow root user to connect from any host
    cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY 'Shra@0303'")
    print("✅ Updated root@localhost user")
    
    # Create root user for all IPs
    try:
        cursor.execute("CREATE USER 'root'@'%' IDENTIFIED BY 'Shra@0303'")
        print("✅ Created root@% user")
    except:
        cursor.execute("ALTER USER 'root'@'%' IDENTIFIED BY 'Shra@0303'")
        print("✅ Updated root@% user (already existed)")
    
    # Grant all privileges
    cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION")
    print("✅ Granted privileges to root@%")
    
    # Flush privileges
    cursor.execute("FLUSH PRIVILEGES")
    print("✅ Flushed privileges")
    
    # Test the connection
    cursor.execute("SHOW VARIABLES LIKE 'bind_address'")
    result = cursor.fetchone()
    print(f"\n📍 Current bind address: {result[1] if result else 'Not found'}")
    
    print("\n✅ MySQL Remote Access Configuration Complete!")
    print("   Users on other computers can now login with:")
    print("   Host: localhost")
    print("   User: root")
    print("   Password: Shra@0303")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
