#!/usr/bin/env python3
"""
Create proper database schema for ReGear with categories and subcategories
"""

import mysql.connector
from mysql.connector import Error

def create_schema():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shra@0303",
            database="regear_db"
        )
        cursor = conn.cursor()
        
        # Drop existing tables if they exist (be careful!)
        # Drop in correct order due to foreign keys
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        cursor.execute("DROP TABLE IF EXISTS listing_images")
        cursor.execute("DROP TABLE IF EXISTS listings")
        cursor.execute("DROP TABLE IF EXISTS subcategories")
        cursor.execute("DROP TABLE IF EXISTS categories")
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        
        print("✅ Dropped old tables")
        
        # Create categories table
        cursor.execute("""
            CREATE TABLE categories (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                icon VARCHAR(20),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created categories table")
        
        # Create subcategories table
        cursor.execute("""
            CREATE TABLE subcategories (
                id INT PRIMARY KEY AUTO_INCREMENT,
                category_id INT NOT NULL,
                name VARCHAR(100) NOT NULL,
                filters JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created subcategories table")
        
        # Create listings table with proper structure
        cursor.execute("""
            CREATE TABLE listings (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                category_id INT NOT NULL,
                subcategory_id INT NOT NULL,
                title VARCHAR(150) NOT NULL,
                description LONGTEXT,
                price INT,
                is_negotiable BOOLEAN DEFAULT FALSE,
                item_condition VARCHAR(50),
                brand VARCHAR(100),
                model VARCHAR(100),
                year_of_purchase INT,
                warranty_available BOOLEAN DEFAULT FALSE,
                
                location VARCHAR(100),
                city VARCHAR(50),
                state VARCHAR(50),
                phone VARCHAR(15),
                email VARCHAR(100),
                
                photos VARCHAR(1000),
                approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                rejection_reason TEXT,
                status ENUM('active', 'sold', 'archived') DEFAULT 'active',
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
                FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE RESTRICT
            )
        """)
        print("✅ Created listings table")
        
        # Create listing_images table
        cursor.execute("""
            CREATE TABLE listing_images (
                id INT PRIMARY KEY AUTO_INCREMENT,
                listing_id INT NOT NULL,
                image_path VARCHAR(500) NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created listing_images table")
        
        # Insert categories
        categories_data = [
            ('Mobile Phones', '📱', 'Smartphones and mobile devices'),
            ('Laptops & Computers', '💻', 'Laptops, desktops, and computers'),
            ('Tablets', '📱', 'Tablet devices and e-readers'),
            ('Computer Accessories', '⌨️', 'Keyboards, mice, cables, and more'),
            ('Printers & Scanners', '🖨️', 'Printers, scanners, and related devices'),
            ('Monitors & Displays', '🖥️', 'Computer monitors and display devices'),
            ('Gaming Consoles', '🎮', 'PlayStation, Xbox, Nintendo devices'),
            ('Smart Watches', '⌚', 'Wearable smart devices'),
            ('Cameras & DSLR', '📷', 'Digital cameras and DSLR equipment'),
            ('Networking Devices', '🌐', 'Routers, WiFi, networking equipment'),
            ('Storage Devices', '💾', 'SSD, HDD, Pendrive, memory cards'),
            ('Speakers & Headphones', '🎧', 'Audio devices and headphones'),
            ('Electronic Components', '🔧', 'Circuit boards, chips, and components'),
            ('TVs & Home Entertainment', '📺', 'Television sets and home theater'),
            ('Smart Home Devices', '🏠', 'Smart home automation devices'),
        ]
        
        for name, icon, desc in categories_data:
            cursor.execute(
                "INSERT INTO categories (name, icon, description) VALUES (%s, %s, %s)",
                (name, icon, desc)
            )
        print(f"✅ Inserted {len(categories_data)} categories")
        
        # Mobile Phones Subcategories
        mobile_subcats = [
            ('Android Phones', None),
            ('iPhones', None),
            ('Keypad Phones', None),
        ]
        
        # Laptops Subcategories
        laptop_subcats = [
            ('Gaming Laptop', '{"processor": ["Intel i5", "Intel i7", "Intel i9", "AMD Ryzen 5", "AMD Ryzen 7"], "ram": ["8GB", "16GB", "32GB"], "storage": ["256GB SSD", "512GB SSD", "1TB SSD"], "gpu": ["NVIDIA GTX", "NVIDIA RTX", "AMD Radeon"]}'),
            ('Business Laptop', '{"processor": ["Intel i5", "Intel i7"], "ram": ["8GB", "16GB"], "storage": ["256GB SSD", "512GB SSD"], "battery": "Good", "weight": "Light"}'),
            ('Student Laptop', '{"processor": ["Intel i5", "Intel i7", "AMD Ryzen 5"], "ram": ["8GB", "16GB"], "storage": ["256GB SSD", "512GB SSD"]}'),
            ('Chromebook', '{"processor": ["Intel", "ARM"], "ram": ["4GB", "8GB"], "storage": ["32GB", "64GB", "128GB"]}'),
            ('MacBook', '{"model": ["MacBook Air", "MacBook Pro", "MacBook"], "processor": ["M1", "M2", "M3", "Intel"], "ram": ["8GB", "16GB", "32GB"]}'),
        ]
        
        # Tablets Subcategories
        tablet_subcats = [
            ('iPad', '{"model": ["iPad Air", "iPad Pro", "iPad Mini"]}'),
            ('Android Tablets', '{"brand": ["Samsung", "OnePlus", "Lenovo"]}'),
            ('Windows Tablets', '{"brand": ["Microsoft", "HP", "Lenovo"]}'),
        ]
        
        # Computer Accessories Subcategories
        accessories_subcats = [
            ('Keyboard', '{"type": ["Mechanical", "Membrane", "Wireless"], "connectivity": ["USB", "Bluetooth"]}'),
            ('Mouse', '{"type": ["Wireless", "Wired", "Gaming"], "dpi": ["Low", "Medium", "High"]}'),
            ('Monitor Stand', '{"adjustable": "Yes/No"}'),
            ('USB Cables', '{"type": ["USB-A", "USB-C", "Micro USB"]}'),
            ('HDMI Cables', '{"length": ["1m", "2m", "3m"]}'),
            ('Chargers', '{"type": ["Wall Charger", "Portable Charger", "Fast Charger"]}'),
        ]
        
        # Printers & Scanners Subcategories
        printer_subcats = [
            ('Inkjet Printer', '{"color": "Yes/No"}'),
            ('Laser Printer', '{"color": "Yes/No"}'),
            ('All-in-One Printer', '{"features": ["Print", "Scan", "Copy"]}'),
            ('Scanner', '{"type": ["Flatbed", "Sheet-fed"]}'),
        ]
        
        # Monitors Subcategories
        monitor_subcats = [
            ('LED Monitor', '{"size": ["21\\"", "23\\"", "24\\"", "27\\"", "32\\""]}'),
            ('Gaming Monitor', '{"refresh_rate": ["60Hz", "120Hz", "144Hz", "165Hz", "240Hz"]}'),
            ('Curved Monitor', '{"curve_radius": "VA"}'),
            ('4K Monitor', '{"resolution": "4K"}'),
        ]
        
        # Gaming Consoles Subcategories
        console_subcats = [
            ('PlayStation', '{"model": ["PS4", "PS5"]}'),
            ('Xbox', '{"model": ["Xbox One", "Xbox Series X", "Xbox Series S"]}'),
            ('Nintendo Switch', '{"type": ["Standard", "Lite", "OLED"]}'),
        ]
        
        # Smart Watches Subcategories
        smartwatch_subcats = [
            ('Apple Watch', '{"series": ["Series 9", "SE", "Ultra"]}'),
            ('Samsung Watch', '{"model": ["Galaxy Watch", "Galaxy Fit"]}'),
            ('Fitbit', '{"type": ["Sense", "Inspire", "Charge"]}'),
            ('Other Smart Watches', '{"brand": ["Garmin", "Amazfit", "Others"]}'),
        ]
        
        # Camera & DSLR Subcategories
        camera_subcats = [
            ('DSLR Camera', '{"brand": ["Canon", "Nikon", "Sony"], "megapixels": ["12MP", "16MP", "20MP", "24MP+"]}'),
            ('Mirrorless Camera', '{"brand": ["Sony", "Canon", "Nikon"]}'),
            ('Point & Shoot Camera', '{"type": ["Compact", "Bridge"]}'),
            ('Camera Lenses', '{"type": ["Prime", "Zoom"]}'),
        ]
        
        # Networking Subcategories
        network_subcats = [
            ('WiFi Router', '{"standard": ["WiFi 5", "WiFi 6", "WiFi 6E"]}'),
            ('WiFi Extender', '{"standard": ["WiFi 5", "WiFi 6"]}'),
            ('Network Cable', '{"type": ["Cat5e", "Cat6", "Cat7"]}'),
            ('Modem', '{"type": ["ADSL", "Cable", "4G"]}'),
        ]
        
        # Storage Devices Subcategories
        storage_subcats = [
            ('SSD (Solid State Drive)', '{"capacity": ["240GB", "256GB", "512GB", "1TB", "2TB"]}'),
            ('HDD (Hard Disk Drive)', '{"capacity": ["500GB", "1TB", "2TB", "4TB"]}'),
            ('USB Pendrive', '{"capacity": ["8GB", "16GB", "32GB", "64GB", "128GB"]}'),
            ('Memory Card', '{"capacity": ["32GB", "64GB", "128GB", "256GB"]}'),
        ]
        
        # Speakers & Headphones Subcategories
        audio_subcats = [
            ('Headphones', '{"type": ["Over-ear", "On-ear", "In-ear"], "connectivity": ["Wired", "Wireless"]}'),
            ('Earbuds', '{"type": ["True Wireless", "Wired"], "noise_cancellation": "Yes/No"}'),
            ('Speakers', '{"type": ["Bluetooth", "Wired", "Smart"]}'),
            ('Microphone', '{"type": ["Condenser", "Dynamic", "Lavalier"]}'),
        ]
        
        # Electronic Components Subcategories
        components_subcats = [
            ('Motherboard', '{"socket": ["LGA 1700", "AM5", "TR4"]}'),
            ('Graphics Card', '{"type": ["NVIDIA", "AMD"], "vram": ["2GB", "4GB", "6GB", "8GB", "12GB"]}'),
            ('Power Supply', '{"wattage": ["500W", "650W", "750W", "1000W"]}'),
            ('RAM Memory', '{"capacity": ["8GB", "16GB", "32GB"], "type": ["DDR3", "DDR4", "DDR5"]}'),
        ]
        
        # TV & Home Entertainment Subcategories
        tv_subcats = [
            ('LED TV', '{"inches": ["32", "43", "50", "55", "65"]}'),
            ('QLED TV', '{"inches": ["55", "65", "75", "85"]}'),
            ('OLED TV', '{"inches": ["55", "65", "77"]}'),
            ('Smart TV', '{"os": ["Android", "WebOS", "Tizen"]}'),
        ]
        
        # Smart Home Subcategories
        smarthome_subcats = [
            ('Smart Lights', '{"type": ["Bulb", "Strip", "Panel"]}'),
            ('Smart Speaker', '{"brand": ["Google", "Amazon", "Apple"]}'),
            ('Smart Thermostat', '{"model": ["Nest", "Ecobee", "Honeywell"]}'),
            ('Security Camera', '{"type": ["Indoor", "Outdoor", "Doorbell"]}'),
        ]
        
        all_subcategories = [
            ('Mobile Phones', mobile_subcats),
            ('Laptops & Computers', laptop_subcats),
            ('Tablets', tablet_subcats),
            ('Computer Accessories', accessories_subcats),
            ('Printers & Scanners', printer_subcats),
            ('Monitors & Displays', monitor_subcats),
            ('Gaming Consoles', console_subcats),
            ('Smart Watches', smartwatch_subcats),
            ('Cameras & DSLR', camera_subcats),
            ('Networking Devices', network_subcats),
            ('Storage Devices', storage_subcats),
            ('Speakers & Headphones', audio_subcats),
            ('Electronic Components', components_subcats),
            ('TVs & Home Entertainment', tv_subcats),
            ('Smart Home Devices', smarthome_subcats),
        ]
        
        total_subcats = 0
        for category_name, subcats in all_subcategories:
            cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
            cat_id = cursor.fetchone()[0]
            
            for subcat_name, filters_data in subcats:
                filters_json = filters_data if isinstance(filters_data, str) else None
                cursor.execute(
                    "INSERT INTO subcategories (category_id, name, filters) VALUES (%s, %s, %s)",
                    (cat_id, subcat_name, filters_json)
                )
                total_subcats += 1
        
        print(f"✅ Inserted {total_subcats} subcategories")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ Database schema created successfully!")
        print("="*60)
        print(f"📊 Summary:")
        print(f"   - Categories: {len(categories_data)}")
        print(f"   - Subcategories: {total_subcats}")
        print(f"   - Tables: categories, subcategories, listings, listing_images")
        print("="*60)
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_schema()
