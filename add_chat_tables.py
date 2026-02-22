import mysql.connector
from mysql.connector import Error

# simple script to create conversation/message/notification tables if not present

def main():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shra@0303",
            database="regear_db"
        )
        cursor = conn.cursor()

        # conversations
        try:
            cursor.execute("""
                CREATE TABLE conversations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    listing_id INT NOT NULL,
                    buyer_id INT NOT NULL,
                    seller_id INT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_message_at DATETIME DEFAULT NULL,
                    UNIQUE KEY uniq_conv (listing_id, buyer_id)
                )
            """)
            print("✅ Created 'conversations' table")
        except Error as e:
            if "exists" in str(e):
                print("⚠️  'conversations' table already exists")
            else:
                print(f"❌ error creating conversations table: {e}")

        # messages
        try:
            cursor.execute("""
                CREATE TABLE messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id INT NOT NULL,
                    sender_id INT NOT NULL,
                    content TEXT,
                    image_path VARCHAR(255),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            print("✅ Created 'messages' table")
        except Error as e:
            if "exists" in str(e):
                print("⚠️  'messages' table already exists")
            else:
                print(f"❌ error creating messages table: {e}")

        # notifications (simple)
        try:
            cursor.execute("""
                CREATE TABLE notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message VARCHAR(255) NOT NULL,
                    is_read TINYINT(1) DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created 'notifications' table")
        except Error as e:
            if "exists" in str(e):
                print("⚠️  'notifications' table already exists")
            else:
                print(f"❌ error creating notifications table: {e}")

        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"❌ Database Error: {e}")

if __name__ == '__main__':
    main()