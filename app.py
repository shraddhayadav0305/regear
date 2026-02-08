from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import mysql.connector
from mysql.connector import Error as MySQLError
import hashlib
from functools import wraps
from datetime import datetime
import secrets
import os
from werkzeug.utils import secure_filename

# Import admin routes
from routes.admin import admin_bp
from routes.categories import categories_bp

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get("REGEAR_SECRET_KEY", "regear_secret_key_secure")
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

DB_CONFIG = {
    "host": os.environ.get("REGEAR_DB_HOST", "localhost"),
    "user": os.environ.get("REGEAR_DB_USER", "root"),
    "password": os.environ.get("REGEAR_DB_PASSWORD", "Shra@0303"),
    "database": os.environ.get("REGEAR_DB_NAME", "regear_db"),
}

# Register admin blueprint
app.register_blueprint(admin_bp)
app.register_blueprint(categories_bp)

# Password hashing utility
def hash_password(password):
    """Hash password using SHA-256 with a salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(stored_hash, password):
    """Verify password against stored hash"""
    try:
        salt, hash_val = stored_hash.split('$')
        return hash_val == hashlib.sha256((salt + password).encode()).hexdigest()
    except:
        # Fallback for plaintext passwords (for existing users)
        return stored_hash == hashlib.sha256(password.encode()).hexdigest() or stored_hash == password


# Database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def is_database_available():
    try:
        conn = get_db_connection()
        conn.close()
        return True
    except MySQLError:
        return False

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first!", "error")
            # send the original path so user can be redirected back after login
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("❌ Admin access only!", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ===========================
# BASIC ROUTES
# ===========================

@app.route("/")
def home():
    return render_template("homepg.html")

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        feedback_type = request.form.get("feedback_type", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not feedback_type or not message:
            flash("❌ Please complete all feedback fields.", "error")
            return redirect(url_for("feedback"))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO feedback (user_id, name, email, feedback_type, message, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (session.get("user_id"), name, email, feedback_type, message, datetime.now()),
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("✅ Thanks for your feedback! We appreciate your help.", "success")
            return redirect(url_for("feedback"))
        except Exception as e:
            flash(f"❌ Error submitting feedback: {str(e)}", "error")
            return redirect(url_for("feedback"))

    return render_template("feedback.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role", "buyer")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        if not username or not email or not password:
            flash("❌ All fields are required", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("❌ Password must be at least 6 characters", "error")
            return redirect(url_for("register"))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # check email
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("❌ Email already registered", "error")
                return redirect(url_for("register"))

            hashed_password = hash_password(password)

            cursor.execute("""
                INSERT INTO users (role, username, email, password, phone, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (role, username, email, hashed_password, phone, datetime.now()))

            conn.commit()
            cursor.close()
            conn.close()

            flash("✅ Registration successful. Please login.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, password, role, username FROM users WHERE email=%s",
                (email,)
            )
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if not user:
                flash("❌ User not found")
                return redirect(url_for("login"))

            user_id, db_password, role, username = user

            if role == "blocked":
                flash("❌ Your account has been blocked. Please contact support.", "error")
                return redirect(url_for("login"))

            if verify_password(db_password, password):

                session["user_id"] = user_id
                session["role"] = role
                session["username"] = username

                flash("✅ Login successful", "success")

                # Redirect back to 'next' if present (safe relative path)
                next_url = request.form.get('next') or request.args.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)

                # ROLE BASED REDIRECT fallback
                if role == "admin":
                    return redirect(url_for("admin.dashboard"))
                else:
                    return redirect(url_for("home"))

            else:
                flash("❌ Wrong password")
                return redirect(url_for("login"))

        except MySQLError as e:
            flash("❌ Database error")
            print(e)
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["reset_email"] = email
            return redirect(url_for("reset_password"))
        else:
            flash("Email not found")

    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "reset_email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form.get("password")

        if not new_password or len(new_password) < 6:
            flash("❌ Password must be at least 6 characters")
            return redirect(url_for("reset_password"))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (hash_password(new_password), session["reset_email"])
        )

        conn.commit()
        cursor.close()
        conn.close()

        session.pop("reset_email")

        flash("Password reset successfully. Please login.")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


@app.route("/dashboard")
@login_required
def dashboard():
    try:
        username = session.get('username', 'User')
        role = session.get('role', 'buyer')
        return render_template("dashboard.html", username=username, role=role)
    except Exception as e:
        flash(f"❌ Error loading dashboard: {str(e)}", "error")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    flash("✅ Logged out successfully!", "success")
    return redirect(url_for("login"))

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "ReGear server is running",
        "database": "connected" if is_database_available() else "disconnected"
    })

@app.route("/api/reverse-geocode")
def reverse_geocode():
    """Convert coordinates to location name"""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    if not lat or not lng:
        return jsonify({"location_name": "Unknown Location"}), 400
    
    # Indian cities and their approximate coordinates
    cities = {
        "Delhi": (28.6139, 77.2090),
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Hyderabad": (17.3850, 78.4867),
        "Chennai": (13.0827, 80.2707),
        "Kolkata": (22.5726, 88.3639),
        "Pune": (18.5204, 73.8567),
        "Ahmedabad": (23.0225, 72.5714),
        "Lucknow": (26.8467, 80.9462),
        "Indore": (22.7196, 75.8577),
        "Kerala": (10.8505, 76.2711),
        "Tamil Nadu": (11.1271, 78.6569),
        "Andhra Pradesh": (15.9129, 78.6675),
        "Telangana": (18.1124, 79.0193),
        "Maharashtra": (19.7515, 75.7139),
        "Gujarat": (22.2587, 71.1924)
    }
    
    # Find closest city
    closest_city = "Unknown Location"
    min_distance = float('inf')
    
    for city, (city_lat, city_lng) in cities.items():
        distance = ((lat - city_lat) ** 2 + (lng - city_lng) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            closest_city = city
    
    return jsonify({"location_name": closest_city})

# ===========================
# CATEGORY & LISTING ROUTES
# ===========================

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """API endpoint to get categories (for frontend) - Electronics & Hardware Only"""
    categories = {
        'Mobiles': {
            'icon': '📱',
            'subcategories': ['iPhone 6', 'iPhone 7', 'iPhone 8', 'iPhone X', 'iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 14', 'iPhone 15',
                            'Samsung Galaxy S6', 'Samsung Galaxy S7', 'Samsung Galaxy S8', 'Samsung Galaxy S9', 'Samsung Galaxy S10', 'Samsung Galaxy S20', 'Samsung Galaxy S21', 'Samsung Galaxy S22', 'Samsung Galaxy S23',
                            'OnePlus 5', 'OnePlus 6', 'OnePlus 7', 'OnePlus 8', 'OnePlus 9', 'OnePlus 10',
                            'Xiaomi Redmi', 'Xiaomi Poco', 'Xiaomi Mi',
                            'Realme 3', 'Realme 5', 'Realme 6', 'Realme 7', 'Realme 8', 'Realme 9',
                            'Oppo A Series', 'Oppo F Series', 'Oppo Reno',
                            'Vivo Y Series', 'Vivo V Series', 'Vivo X Series',
                            'Motorola G Series', 'Motorola E Series',
                            'Nokia Lumia', 'Nokia Android',
                            'Google Pixel', 'Google Nexus',
                            'Sony Xperia', 'HTC', 'LG G Series',
                            'Mobile Accessories', 'Phone Chargers', 'Screen Protectors', 'Phone Cases', 'Power Banks', 'Phone Stands', 'Tempered Glass']
        },
        'Laptops & Computers': {
            'icon': '💻',
            'subcategories': ['Gaming Laptops', 'Business Laptops', 'MacBooks', 'Ultrabooks', 'Budget Laptops', 'Desktop Computers', 'Gaming PCs', 'All-in-One PCs', 'Mini PCs', 'Workstations', 'Tablets', 'iPads', 'Android Tablets']
        },
        'Computer Hardware': {
            'icon': '⚙️',
            'subcategories': ['Graphics Cards (GPU)', 'Processors (CPU)', 'Motherboards', 'RAM Memory', 'Solid State Drives (SSD)', 'Hard Disk Drives (HDD)', 'Power Supply Units', 'CPU Coolers', 'Computer Cases', 'Fans & Cooling', 'BIOS Chips', 'Server Hardware', 'Networking Cards']
        },
        'Peripherals & Accessories': {
            'icon': '⌨️',
            'subcategories': ['Mechanical Keyboards', 'Gaming Keyboards', 'Wireless Keyboards', 'Computer Mouse', 'Gaming Mouse', 'Trackpads', 'Monitor Stands', 'Cable Organizers', 'USB Hubs', 'Cables & Adapters', 'HDMI Cables', 'USB Cables', 'Ethernet Cables', 'Docking Stations']
        },
        'Monitors & Displays': {
            'icon': '🖥️',
            'subcategories': ['Gaming Monitors', '4K Monitors', 'IPS Monitors', 'TN Monitors', 'VA Monitors', 'Curved Monitors', 'Portable Monitors', 'LED Displays', 'Professional Monitors', 'Monitor Arms', 'Monitor Stands']
        },
        'Audio & Sound': {
            'icon': '🎧',
            'subcategories': ['Headphones', 'Earbuds', 'Wireless Earbuds', 'Gaming Headsets', 'Studio Headphones', 'Noise Cancelling Headphones', 'Speakers', 'Bluetooth Speakers', 'Studio Monitors', 'Subwoofers', 'Microphones', 'Audio Interfaces', 'Amplifiers']
        },
        'Cameras & Optics': {
            'icon': '📷',
            'subcategories': ['DSLR Cameras', 'Mirrorless Cameras', 'Digital Cameras', 'Action Cameras', 'Instant Cameras', 'Film Cameras', 'Camera Lenses', 'Camera Tripods', 'Camera Stands', 'Camera Bags', 'Lighting Equipment', 'Ring Lights', 'Studio Lights', 'Reflectors']
        },
        'Printers & Scanners': {
            'icon': '🖨️',
            'subcategories': ['Inkjet Printers', 'Laser Printers', 'All-in-One Printers', 'Photo Printers', '3D Printers', 'Document Scanners', 'Flatbed Scanners', 'Printer Cartridges', 'Toner Cartridges', 'Printer Paper', 'Ink Supplies']
        },
        'Gaming Hardware': {
            'icon': '🎮',
            'subcategories': ['Gaming Consoles', 'PlayStation', 'Xbox', 'Nintendo Switch', 'Gaming Controllers', 'VR Headsets', 'Gaming Chairs', 'Racing Wheels', 'Arcade Sticks', 'Gaming Desks', 'Gaming Lamps']
        },
        'Networking Equipment': {
            'icon': '🌐',
            'subcategories': ['WiFi Routers', 'WiFi 6 Routers', 'Mesh WiFi Systems', 'Modems', 'Network Switches', 'Network Cables', 'WiFi Extenders', 'Wireless Access Points', 'Network Adapters', 'Ethernet Hubs']
        },
        'Smart Devices & IoT': {
            'icon': '🔌',
            'subcategories': ['Smart Watches', 'Fitness Trackers', 'Smart Home Hubs', 'Smart Speakers', 'Smart Thermostats', 'Smart Lights', 'Smart Plugs', 'Smart Locks', 'Smart Door Bells', 'Security Cameras', 'Smart Displays']
        },
        'TVs & Displays': {
            'icon': '📺',
            'subcategories': ['LED TVs', 'QLED TVs', 'Smart TVs', 'OLED TVs', 'Mini LED TVs', '4K TVs', '8K TVs', 'Curved TVs', 'Portable Projectors', 'Home Projectors', 'TV Stands', 'TV Wall Mounts']
        },
        'Kitchen Appliances': {
            'icon': '🍳',
            'subcategories': ['Refrigerators', 'Microwave Ovens', 'Electric Ovens', 'Dishwashers', 'Washing Machines', 'Washing Machine Drums', 'Dryers', 'Air Fryers', 'Electric Cookers', 'Blenders', 'Mixer Grinders', 'Juicers', 'Coffee Makers', 'Toasters', 'Water Purifiers', 'Electric Kettles', 'Rice Cookers']
        },
        'Home Appliances': {
            'icon': '❄️',
            'subcategories': ['Air Conditioners', 'Air Coolers', 'Fans', 'Heaters', 'Humidifiers', 'Dehumidifiers', 'Vacuum Cleaners', 'Air Purifiers', 'Water Heaters', 'Geysers', 'Inverters', 'Solar Panels', 'Solar Batteries']
        },
        'Electronic Components': {
            'icon': '🔧',
            'subcategories': ['Semiconductors', 'Integrated Circuits', 'Transistors', 'Capacitors', 'Resistors', 'Diodes', 'LED Components', 'Connectors', 'Switches', 'Relays', 'Transformers', 'Circuit Boards (PCB)', 'Cooling Compounds', 'Thermal Paste', 'Solder & Flux']
        },
        'Testing & Tools': {
            'icon': '🔍',
            'subcategories': ['Digital Multimeters', 'Oscilloscopes', 'Power Supplies (Lab)', 'Soldering Irons', 'Heat Guns', 'Logic Analyzers', 'Network Testers', 'Thermal Cameras', 'Clamp Meters', 'Tool Kits', 'Cable Testers', 'RF Meters']
        },
        'Batteries & Power': {
            'icon': '🔋',
            'subcategories': ['Lithium Ion Batteries', 'Lithium Polymer Batteries', 'Lead Acid Batteries', 'Ni-MH Batteries', 'Battery Packs', 'UPS Units', 'Power Banks', 'Charging Cables', 'Battery Chargers', 'Solar Chargers', 'Car Chargers', 'Fast Chargers']
        },
        'Networking Cables': {
            'icon': '🧵',
            'subcategories': ['Ethernet Cables (Cat5e)', 'Ethernet Cables (Cat6)', 'Ethernet Cables (Cat7)', 'Fiber Optic Cables', 'HDMI Cables', 'USB Cables (Type A)', 'USB Cables (Type C)', 'USB Cables (Lightning)', 'Audio Cables', 'Video Cables', 'Power Cables', 'Coaxial Cables']
        }
    }
    return jsonify(categories)

@app.route("/sell")
def sell():
    """Show combined category & subcategory selection page for selling items"""
    return render_template("categories_combined.html")

@app.route("/subcategories")
def subcategories():
    """Show subcategories for selected category"""
    category = request.args.get('category')
    
    categories = {
        'Mobiles': {
            'icon': '📱',
            'subcategories': ['iPhone 6', 'iPhone 7', 'iPhone 8', 'iPhone X', 'iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 14', 'iPhone 15',
                            'Samsung Galaxy S6', 'Samsung Galaxy S7', 'Samsung Galaxy S8', 'Samsung Galaxy S9', 'Samsung Galaxy S10', 'Samsung Galaxy S20', 'Samsung Galaxy S21', 'Samsung Galaxy S22', 'Samsung Galaxy S23',
                            'OnePlus 5', 'OnePlus 6', 'OnePlus 7', 'OnePlus 8', 'OnePlus 9', 'OnePlus 10',
                            'Xiaomi Redmi', 'Xiaomi Poco', 'Xiaomi Mi',
                            'Realme 3', 'Realme 5', 'Realme 6', 'Realme 7', 'Realme 8', 'Realme 9',
                            'Oppo A Series', 'Oppo F Series', 'Oppo Reno',
                            'Vivo Y Series', 'Vivo V Series', 'Vivo X Series',
                            'Motorola G Series', 'Motorola E Series',
                            'Nokia Lumia', 'Nokia Android',
                            'Google Pixel', 'Google Nexus',
                            'Sony Xperia', 'HTC', 'LG G Series',
                            'Mobile Accessories', 'Phone Chargers', 'Screen Protectors', 'Phone Cases', 'Power Banks', 'Phone Stands', 'Tempered Glass']
        },
        'Laptops & Computers': {
            'icon': '💻',
            'subcategories': ['Gaming Laptops', 'Business Laptops', 'MacBooks', 'Ultrabooks', 'Budget Laptops', 'Desktop Computers', 'Gaming PCs', 'All-in-One PCs', 'Mini PCs', 'Workstations', 'Tablets', 'iPads', 'Android Tablets']
        },
        'Computer Hardware': {
            'icon': '⚙️',
            'subcategories': ['Graphics Cards (GPU)', 'Processors (CPU)', 'Motherboards', 'RAM Memory', 'Solid State Drives (SSD)', 'Hard Disk Drives (HDD)', 'Power Supply Units', 'CPU Coolers', 'Computer Cases', 'Fans & Cooling', 'BIOS Chips', 'Server Hardware', 'Networking Cards']
        },
        'Peripherals & Accessories': {
            'icon': '⌨️',
            'subcategories': ['Mechanical Keyboards', 'Gaming Keyboards', 'Wireless Keyboards', 'Computer Mouse', 'Gaming Mouse', 'Trackpads', 'Monitor Stands', 'Cable Organizers', 'USB Hubs', 'Cables & Adapters', 'HDMI Cables', 'USB Cables', 'Ethernet Cables', 'Docking Stations']
        },
        'Monitors & Displays': {
            'icon': '🖥️',
            'subcategories': ['Gaming Monitors', '4K Monitors', 'IPS Monitors', 'TN Monitors', 'VA Monitors', 'Curved Monitors', 'Portable Monitors', 'LED Displays', 'Professional Monitors', 'Monitor Arms', 'Monitor Stands']
        },
        'Audio & Sound': {
            'icon': '🎧',
            'subcategories': ['Headphones', 'Earbuds', 'Wireless Earbuds', 'Gaming Headsets', 'Studio Headphones', 'Noise Cancelling Headphones', 'Speakers', 'Bluetooth Speakers', 'Studio Monitors', 'Subwoofers', 'Microphones', 'Audio Interfaces', 'Amplifiers']
        },
        'Cameras & Optics': {
            'icon': '📷',
            'subcategories': ['DSLR Cameras', 'Mirrorless Cameras', 'Digital Cameras', 'Action Cameras', 'Instant Cameras', 'Film Cameras', 'Camera Lenses', 'Camera Tripods', 'Camera Stands', 'Camera Bags', 'Lighting Equipment', 'Ring Lights', 'Studio Lights', 'Reflectors']
        },
        'Printers & Scanners': {
            'icon': '🖨️',
            'subcategories': ['Inkjet Printers', 'Laser Printers', 'All-in-One Printers', 'Photo Printers', '3D Printers', 'Document Scanners', 'Flatbed Scanners', 'Printer Cartridges', 'Toner Cartridges', 'Printer Paper', 'Ink Supplies']
        },
        'Gaming Hardware': {
            'icon': '🎮',
            'subcategories': ['Gaming Consoles', 'PlayStation', 'Xbox', 'Nintendo Switch', 'Gaming Controllers', 'VR Headsets', 'Gaming Chairs', 'Racing Wheels', 'Arcade Sticks', 'Gaming Desks', 'Gaming Lamps']
        },
        'Networking Equipment': {
            'icon': '🌐',
            'subcategories': ['WiFi Routers', 'WiFi 6 Routers', 'Mesh WiFi Systems', 'Modems', 'Network Switches', 'Network Cables', 'WiFi Extenders', 'Wireless Access Points', 'Network Adapters', 'Ethernet Hubs']
        },
        'Smart Devices & IoT': {
            'icon': '🔌',
            'subcategories': ['Smart Watches', 'Fitness Trackers', 'Smart Home Hubs', 'Smart Speakers', 'Smart Thermostats', 'Smart Lights', 'Smart Plugs', 'Smart Locks', 'Smart Door Bells', 'Security Cameras', 'Smart Displays']
        },
        'TVs & Displays': {
            'icon': '📺',
            'subcategories': ['LED TVs', 'QLED TVs', 'Smart TVs', 'OLED TVs', 'Mini LED TVs', '4K TVs', '8K TVs', 'Curved TVs', 'Portable Projectors', 'Home Projectors', 'TV Stands', 'TV Wall Mounts']
        },
        'Kitchen Appliances': {
            'icon': '🍳',
            'subcategories': ['Refrigerators', 'Microwave Ovens', 'Electric Ovens', 'Dishwashers', 'Washing Machines', 'Washing Machine Drums', 'Dryers', 'Air Fryers', 'Electric Cookers', 'Blenders', 'Mixer Grinders', 'Juicers', 'Coffee Makers', 'Toasters', 'Water Purifiers', 'Electric Kettles', 'Rice Cookers']
        },
        'Home Appliances': {
            'icon': '❄️',
            'subcategories': ['Air Conditioners', 'Air Coolers', 'Fans', 'Heaters', 'Humidifiers', 'Dehumidifiers', 'Vacuum Cleaners', 'Air Purifiers', 'Water Heaters', 'Geysers', 'Inverters', 'Solar Panels', 'Solar Batteries']
        },
        'Electronic Components': {
            'icon': '🔧',
            'subcategories': ['Semiconductors', 'Integrated Circuits', 'Transistors', 'Capacitors', 'Resistors', 'Diodes', 'LED Components', 'Connectors', 'Switches', 'Relays', 'Transformers', 'Circuit Boards (PCB)', 'Cooling Compounds', 'Thermal Paste', 'Solder & Flux']
        },
        'Testing & Tools': {
            'icon': '🔍',
            'subcategories': ['Digital Multimeters', 'Oscilloscopes', 'Power Supplies (Lab)', 'Soldering Irons', 'Heat Guns', 'Logic Analyzers', 'Network Testers', 'Thermal Cameras', 'Clamp Meters', 'Tool Kits', 'Cable Testers', 'RF Meters']
        },
        'Batteries & Power': {
            'icon': '🔋',
            'subcategories': ['Lithium Ion Batteries', 'Lithium Polymer Batteries', 'Lead Acid Batteries', 'Ni-MH Batteries', 'Battery Packs', 'UPS Units', 'Power Banks', 'Charging Cables', 'Battery Chargers', 'Solar Chargers', 'Car Chargers', 'Fast Chargers']
        },
        'Networking Cables': {
            'icon': '🧵',
            'subcategories': ['Ethernet Cables (Cat5e)', 'Ethernet Cables (Cat6)', 'Ethernet Cables (Cat7)', 'Fiber Optic Cables', 'HDMI Cables', 'USB Cables (Type A)', 'USB Cables (Type C)', 'USB Cables (Lightning)', 'Audio Cables', 'Video Cables', 'Power Cables', 'Coaxial Cables']
        }
    }
    
    if category not in categories:
        flash("❌ Invalid category", "error")
        return redirect(url_for("sell"))
    
    return render_template("subcategories.html", category=category, subcategories=categories[category]['subcategories'])

@app.route("/save-category", methods=["POST"])
@login_required
def save_category():
    """Save category selection to session"""
    try:
        data = request.get_json()
        category = data.get('category')
        subcategory = data.get('subcategory')
        
        if not category or not subcategory:
            return jsonify({"success": False, "message": "Invalid selection"}), 400
        
        session['selected_category'] = category
        session['selected_subcategory'] = subcategory
        
        return jsonify({"success": True, "message": "Category saved", "redirect_url": url_for("post_ad_form")})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/post-ad-form", methods=["GET", "POST"])
@login_required
def post_ad_form():
    """Handle ad posting form"""
    if request.method == "POST":
        app.logger.info(f"POST /post-ad-form called by session user_id={session.get('user_id')}")
        try:
            user_id = session.get('user_id')
            category = request.form.get('category')
            subcategory = request.form.get('subcategory')
            title = request.form.get('title')
            description = request.form.get('description')
            price = request.form.get('price')
            location = request.form.get('location')
            phone = request.form.get('phone')
            email = request.form.get('email')
            condition = request.form.get('condition')  # New/Used
            
            # Basic required validation
            if not all([category, subcategory, title, description, price, condition]):
                flash("❌ All required fields must be filled (title, category, price, condition, description)", "error")
                return redirect(url_for("post_ad_form"))

            # Handle photo uploads - require at least one image
            uploaded_files = request.files.getlist('photos')
            if not uploaded_files or len([f for f in uploaded_files if f and f.filename]) == 0:
                flash("❌ Please upload at least one image (JPG/PNG)", "error")
                return redirect(url_for("post_ad_form"))

            saved_paths = []
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'products')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, exist_ok=True)

            ALLOWED_EXT = {'jpg', 'jpeg', 'png'}
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

            # Prevent duplicate quick submissions: same user, same title within last 60 seconds
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, created_at FROM listings WHERE user_id=%s AND title=%s ORDER BY created_at DESC LIMIT 1", (user_id, title))
            last = cursor.fetchone()
            if last:
                try:
                    last_time = last[1]
                    if (datetime.now() - last_time).total_seconds() < 60:
                        cursor.close()
                        conn.close()
                        flash("⚠️ Duplicate submission detected. Please wait a moment before retrying.", "warning")
                        return redirect(url_for("post_ad_form"))
                except Exception:
                    pass

            for f in uploaded_files:
                if f and f.filename:
                    if not allowed_file(f.filename):
                        flash("❌ Only JPG/JPEG/PNG images are allowed", "error")
                        cursor.close()
                        conn.close()
                        return redirect(url_for("post_ad_form"))

                    filename = secure_filename(f.filename)
                    unique_name = secrets.token_hex(12) + '_' + filename
                    dest = os.path.join(upload_dir, unique_name)
                    f.save(dest)
                    rel_path = os.path.join('static', 'uploads', 'products', unique_name).replace('\\', '/')
                    saved_paths.append(rel_path)

            photos_str = ','.join(saved_paths)

            # Insert listing with pending approval
            cursor.execute("""
                INSERT INTO listings (user_id, category, subcategory, title, description, price, location, phone, email, item_condition, photos, created_at, status, approval_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, category, subcategory, title, description, price, location, phone, email, condition, photos_str, datetime.now(), 'pending', 'pending'))

            conn.commit()
            listing_id = cursor.lastrowid

            # Save individual images to product_images table if exists
            try:
                for p in saved_paths:
                    cursor.execute("INSERT INTO product_images (listing_id, image_path, created_at) VALUES (%s, %s, NOW())", (listing_id, p))
                conn.commit()
            except Exception:
                # ignore if table missing; product_images migration handled separately
                pass

            cursor.close()
            conn.close()

            flash("Your ad has been submitted and is under admin review.", "success")
            return redirect(url_for("my_listings"))
            
        except Exception as e:
            flash(f"❌ Error posting ad: {str(e)}", "error")
            return redirect(url_for("post_ad_form"))
    
    # Get selected category from session
    selected_category = session.get('selected_category', '')
    selected_subcategory = session.get('selected_subcategory', '')
    
    return render_template("addpost.html", selected_category=selected_category, selected_subcategory=selected_subcategory)

@app.route("/my-listings")
@login_required
def my_listings():
    """View my listings (for sellers)"""
    try:
        user_id = session.get('user_id')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, title, category, price, status, created_at 
            FROM listings 
            WHERE user_id=%s 
            ORDER BY created_at DESC
        """, (user_id,))
        
        listings = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template("my_listings.html", listings=listings)
        
    except Exception as e:
        flash(f"❌ Error loading listings: {str(e)}", "error")
        return redirect(url_for("dashboard"))

@app.route("/browse")
def browse():
    """Browse all listings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, title, category, subcategory, price, location, created_at 
            FROM listings 
            WHERE approval_status='approved'
            ORDER BY created_at DESC
        """)
        
        listings = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template("browse_listings.html", listings=listings)
        
    except Exception as e:
        flash(f"❌ Error loading listings: {str(e)}", "error")
        return redirect(url_for("home"))

@app.route("/listing/<int:listing_id>")
def view_listing(listing_id):
    """View individual listing details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT l.*, u.username, u.phone as seller_phone, u.email as seller_email
            FROM listings l
            JOIN users u ON l.user_id = u.id
            WHERE l.id=%s
        """, (listing_id,))
        
        listing = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not listing:
            flash("❌ Listing not found", "error")
            return redirect(url_for("browse"))

        # Only public if admin-approved, unless owner or admin
        if listing.get('approval_status') != 'approved':
            current = session.get('user_id')
            if not current or (current != listing.get('user_id') and session.get('role') != 'admin'):
                flash("❌ Listing not available", "error")
                return redirect(url_for("browse"))

        # Use product_detail template
        return render_template("product_detail.html", listing=listing)
        
    except Exception as e:
        flash(f"❌ Error loading listing: {str(e)}", "error")
        return redirect(url_for("browse"))

@app.route("/saved")
@login_required
def saved_items():
    """View saved items"""
    flash("Saved items page coming soon!", "info")
    return redirect(url_for("dashboard"))

@app.route("/orders")
@login_required
def orders():
    """View orders (for buyers)"""
    flash("Orders page coming soon!", "info")
    return redirect(url_for("dashboard"))

@app.route("/post-item")
@login_required
def post_item():
    """Post new item (for sellers) - Redirect to sell page"""
    return redirect(url_for("sell"))

@app.route("/analytics")
@login_required
def analytics():
    """View sales analytics (for sellers)"""
    flash("Analytics page coming soon!", "info")
    return redirect(url_for("dashboard"))

# ==========================
# ADMIN PANEL ROUTES
# ==========================

@app.route("/admin")
@admin_required
def admin_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as buyers FROM users WHERE role='buyer'")
        buyers = cursor.fetchone()["buyers"]

        cursor.execute("SELECT COUNT(*) as sellers FROM users WHERE role='seller'")
        sellers = cursor.fetchone()["sellers"]

        cursor.close()
        conn.close()

        return render_template(
            "admin/admin_dashboard.html",
            total_users=total_users,
            buyers=buyers,
            sellers=sellers
        )
    except Exception as e:
        flash(f"❌ Error loading admin dashboard: {str(e)}", "error")
        return redirect(url_for("dashboard"))


@app.route("/admin/users")
@admin_required
def admin_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, role, created_at FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("admin/admin_users.html", users=users)
    except Exception as e:
        flash(f"❌ Error loading users: {str(e)}", "error")
        return redirect(url_for("dashboard"))


@app.route("/admin/block/<int:user_id>")
@admin_required
def block_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role='blocked' WHERE id=%s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("✅ User blocked successfully", "success")
    except Exception as e:
        flash(f"❌ Error blocking user: {str(e)}", "error")
    
    return redirect(url_for("admin_users"))


@app.route("/admin/unblock/<int:user_id>")
@admin_required
def unblock_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role='buyer' WHERE id=%s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("✅ User unblocked successfully", "success")
    except Exception as e:
        flash(f"❌ Error unblocking user: {str(e)}", "error")
    
    return redirect(url_for("admin_users"))


# ==========================
# ERROR HANDLERS
# ==========================

@app.errorhandler(404)
def not_found(error):
    return redirect(url_for("home"))

@app.errorhandler(500)
def server_error(error):
    flash("❌ Server error! Please try again.", "error")
    return redirect(url_for("home"))

if __name__ == "__main__":
    import sys
    import io
    # Fix Unicode encoding for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("🚀 Starting ReGear Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📝 Register: http://localhost:5000/register")
    print("🔐 Login: http://localhost:5000/login")
    print("🛍️ Sell: http://localhost:5000/sell")
    app.run(debug=False, host='localhost', port=5000, use_reloader=False)
