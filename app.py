from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import mysql.connector
from mysql.connector import Error as MySQLError
import hashlib
from functools import wraps
from datetime import datetime, timedelta
import secrets
import os
from werkzeug.utils import secure_filename

# Import admin routes
from routes.admin import admin_bp
from routes.categories import categories_bp

app = Flask(__name__, template_folder='templates')
app.secret_key = "regear_secret_key_secure"
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

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
    # Read DB credentials from environment with safe defaults for local dev
    host = os.environ.get('REGEAR_DB_HOST', 'localhost')
    user = os.environ.get('REGEAR_DB_USER', 'root')
    password = os.environ.get('REGEAR_DB_PASSWORD', 'Shra@0303')
    database = os.environ.get('REGEAR_DB_NAME', 'regear_db')

    try:
        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
    except MySQLError as e:
        app.logger.error(f"DB connection failed (host={host} user={user} db={database}): {e}")
        # Re-raise so callers can handle the exception and show user-friendly messages
        raise

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
    """Home page with featured approved listings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT l.id, l.title, l.category, l.subcategory, l.price, l.location, l.created_at, l.photos, u.username
                FROM listings l
                JOIN users u ON l.user_id = u.id
                JOIN ad_boosts b ON b.ad_id=l.id AND b.status='active' AND b.expiry_date>NOW()
                JOIN boost_packages p ON p.id=b.package_id
                WHERE l.approval_status='approved' AND l.status='active' AND p.boost_type IN ('homepage_featured','premium')
                ORDER BY b.expiry_date DESC
                LIMIT 12
            """)
            featured_listings = cursor.fetchall()
        except Exception:
            featured_listings = []
        if not featured_listings:
            try:
                cursor.execute("""
                    SELECT l.id, l.title, l.category, l.subcategory, l.price, l.location, l.created_at, l.photos, u.username
                    FROM listings l
                    JOIN users u ON l.user_id = u.id
                    WHERE l.approval_status='approved' AND l.status='active'
                    ORDER BY l.created_at DESC
                    LIMIT 12
                """)
            except Exception:
                cursor.execute("""
                    SELECT l.id, l.title, l.category, l.subcategory, l.price, '' AS location, l.created_at, l.photos, u.username
                    FROM listings l
                    JOIN users u ON l.user_id = u.id
                    WHERE l.approval_status='approved' AND l.status='active'
                    ORDER BY l.created_at DESC
                    LIMIT 12
                """)
            featured_listings = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("homepg.html", featured_listings=featured_listings)
    except Exception as e:
        print(f"Error loading featured listings: {e}")
        return render_template("homepg.html", featured_listings=[])


# fee mapping for seller packages (package -> ₹ fee)
PACKAGE_FEES = {
    "10": 199.00,
    "15": 349.00,
    "20": 499.00,
}

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        phone = (request.form.get("phone") or "").strip()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("password_confirm") or request.form.get("confirm_password")

        if not full_name or not email or not phone or not password or not confirm_password:
            flash("❌ All fields are required", "error")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("❌ Passwords do not match", "error")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("❌ Password must be at least 6 characters", "error")
            return redirect(url_for("register"))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("❌ Email already registered", "error")
                cursor.close()
                conn.close()
                return redirect(url_for("register"))
            try:
                cursor.execute("SELECT id FROM users WHERE phone=%s", (phone,))
                if cursor.fetchone():
                    flash("❌ Phone number already registered", "error")
                    cursor.close()
                    conn.close()
                    return redirect(url_for("register"))
            except Exception:
                pass
            hashed_password = hash_password(password)
            # Prefer schema with full_name and role; fall back gracefully to older schemas
            try:
                cursor.execute("""
                    INSERT INTO users (username, full_name, email, phone, password, role, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (full_name, full_name, email, phone, hashed_password, 'buyer', datetime.now()))
            except Exception:
                try:
                    cursor.execute("""
                        INSERT INTO users (username, full_name, email, phone, password, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (full_name, full_name, email, phone, hashed_password, datetime.now()))
                except Exception:
                    cursor.execute("""
                        INSERT INTO users (username, email, phone, password, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (full_name, email, phone, hashed_password, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            flash("✅ Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for("register"))
    return render_template("register_unified.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id, password, role, username, profile_photo, profile_image FROM users WHERE email=%s", (email,))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            if not row:
                flash("❌ User not found")
                return redirect(url_for("login"))

            user_id = row["id"]
            db_password = row["password"]
            role = row["role"]
            username = row["username"]
            profile_photo = row.get("profile_photo") or row.get("profile_image")

            if role == "blocked":
                flash("❌ Your account has been blocked. Please contact support.", "error")
                return redirect(url_for("login"))

            if verify_password(db_password, password):

                session["user_id"] = user_id
                session["role"] = role
                session["username"] = username
                session["profile_photo"] = profile_photo

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

        conn = get_db_connection()
        cursor = conn.cursor()

        # Hash and store the new password
        hashed_password = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (hashed_password, session["reset_email"])
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
        user_id = session.get('user_id')
        username = session.get('username', 'User')
        role = session.get('role', 'buyer')
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        # Stats
        try:
            cur.execute("SELECT COUNT(*) AS c FROM listings WHERE user_id=%s AND status='active' AND approval_status='approved'", (user_id,))
            active = cur.fetchone()['c']
        except Exception:
            active = 0
        try:
            cur.execute("SELECT COUNT(*) AS c FROM listings WHERE user_id=%s AND status='sold'", (user_id,))
            sold = cur.fetchone()['c']
        except Exception:
            sold = 0
        try:
            cur.execute("SELECT COUNT(*) AS c FROM listings WHERE user_id=%s AND (status='expired' OR (expires_date IS NOT NULL AND expires_date<NOW() AND COALESCE(is_sold,0)=0))", (user_id,))
            expired = cur.fetchone()['c']
        except Exception:
            expired = 0
        try:
            cur.execute("SELECT COALESCE(SUM(view_count),0) AS v FROM listings WHERE user_id=%s", (user_id,))
            views = cur.fetchone()['v']
        except Exception:
            views = 0
        # Recent listings
        recent_listings = []
        try:
            cur.execute("SELECT id, title, price, status, approval_status, photos, created_at FROM listings WHERE user_id=%s ORDER BY created_at DESC LIMIT 5", (user_id,))
            recent_listings = cur.fetchall()
        except Exception:
            recent_listings = []
        cur.close()
        conn.close()
        stats = {"active": active, "sold": sold, "expired": expired, "views": views}
        return render_template("dashboard.html", username=username, role=role, stats=stats, recent_listings=recent_listings)
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
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return jsonify({
        "status": "ok",
        "message": "ReGear server is running",
        "database": db_status
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
    """API endpoint to get categories from database with images"""
    
    def create_svg_placeholder(cat_name, color):
        """Create SVG placeholder with category name"""
        svg = f'''<svg width="150" height="150" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{color}dd;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="150" height="150" fill="url(#grad)"/>
            <text x="75" y="75" font-size="11" font-weight="bold" fill="white" text-anchor="middle" dominant-baseline="middle" 
                  font-family="Arial, sans-serif" word-spacing="2" lengthAdjust="spacing" textLength="140">
                {cat_name}
            </text>
        </svg>'''
        import base64
        svg_encoded = base64.b64encode(svg.encode()).decode()
        return f"data:image/svg+xml;base64,{svg_encoded}"
    
    # Category image mapping - using local SVG placeholders with colors
    category_images = {
        "Mobile Phones": "/static/images/mobile phones.png",  # custom mobile phone image
        "Laptops & Computers": "/static/images/lap.png",  # custom laptop image
        "Cameras & DSLR": "/static/images/dslr-camera-logo-design-png.png",  # User's camera image
        "TVs & Home Entertainment": "/static/images/tv and ho.png",
        "Gaming Consoles": "/static/images/gaming console.png",  # user image for gaming consoles
        "Speakers & Headphones": "/static/images/speakers and headphones.jpg",
        "Computer Accessories": "/static/images/computer accessories.png",  # User's computer accessories image
        # if user supplies a custom image, serve the file; otherwise fall back to SVG placeholder
        "Electronic Components": "/static/images/electronic component.jpg",  # custom image placed by user
        "Tablets": "/static/images/tablets.webp",
        "Smart Watches": "/static/images/smart watches.jpg",
        "Printers & Scanners": "/static/images/printers and moniters.png",
        "Monitors & Displays": "/static/images/Monitors & Displays.webp",  # custom monitors image
        "Smart Home Devices": "/static/images/Smart-Home-Device-Smart-Device.png",
        "Networking Devices": "/static/images/Screenshot 2026-02-22 193118.png",
        "Storage Devices": "/static/images/storage device.webp"
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, icon FROM categories ORDER BY name")
        categories = cursor.fetchall()
        
        result = {}
        for cat in categories:
            cat_id = cat['id']
            cat_name = cat['name']
            # Fetch subcategories for this category
            cursor.execute(
                "SELECT id, name FROM subcategories WHERE category_id = %s ORDER BY name",
                (cat_id,)
            )
            subcats = cursor.fetchall()
            
            # Get image or create one if not in mapping
            cat_image = category_images.get(cat_name)
            if not cat_image:
                # Create SVG for unmapped categories
                default_color = "#7c3aed"  # Purple fallback
                cat_image = create_svg_placeholder(f"📦 {cat_name}", default_color)
            
            result[cat_name] = {
                'icon': cat['icon'],
                'image': cat_image,
                'id': cat_id,
                'subcategories': [{'id': s['id'], 'name': s['name']} for s in subcats]
            }
        
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sell")
def sell():
    """Show category selection page for selling items"""
    return render_template("categories.html")

@app.route("/subcategories")
def subcategories():
    """Show subcategories for selected category"""
    category_name = request.args.get('category')
    
    if not category_name:
        flash("❌ No category selected", "error")
        return redirect(url_for("sell"))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get category ID
        cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
        result = cursor.fetchone()
        
        if not result:
            flash("❌ Invalid category", "error")
            cursor.close()
            conn.close()
            return redirect(url_for("sell"))
        
        category_id = result['id']
        
        # Get subcategories for this category
        cursor.execute(
            "SELECT id, name FROM subcategories WHERE category_id = %s ORDER BY name",
            (category_id,)
        )
        subcategories_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template("subcategories.html", 
                             category=category_name, 
                             category_id=category_id,
                             subcategories=subcategories_list)
    except Exception as e:
        flash(f"❌ Error loading subcategories: {str(e)}", "error")
        return redirect(url_for("sell"))

@app.route("/save-category", methods=["POST"])
@login_required
def save_category():
    """Save category selection to session"""
    try:
        data = request.get_json()
        category = data.get('category')
        category_id = data.get('category_id')
        subcategory = data.get('subcategory')
        subcategory_id = data.get('subcategory_id')
        
        if not all([category, subcategory, category_id, subcategory_id]):
            return jsonify({"success": False, "message": "Invalid selection"}), 400
        
        session['selected_category'] = category
        session['selected_category_id'] = category_id
        session['selected_subcategory'] = subcategory
        session['selected_subcategory_id'] = subcategory_id
        
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

            # Handle photo uploads - require at least one image (max 8)
            uploaded_files = request.files.getlist('photos')
            valid_files = [f for f in uploaded_files if f and f.filename]
            if not valid_files:
                flash("❌ Please upload at least one image (JPG/PNG)", "error")
                return redirect(url_for("post_ad_form"))
            if len(valid_files) > 8:
                flash("❌ You can upload up to 8 images only", "error")
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

            for f in valid_files:
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

            # Insert listing with pending approval and 5-day free trial visibility
            trial_expires = datetime.now() + timedelta(days=5)
            cursor.execute("""
                INSERT INTO listings (user_id, category, subcategory, title, description, price, location, phone, email, item_condition, photos, created_at, status, approval_status, expires_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, category, subcategory, title, description, price, location, phone, email, condition, photos_str, datetime.now(), 'active', 'pending', trial_expires))

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

            flash("✅ Your ad has been submitted successfully! It's now pending admin review. Once approved, it will be published on the website.", "success")
            return redirect(url_for("dashboard"))
            
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
    try:
        user_id = session.get('user_id')
        username = session.get('username', 'User')
        role = session.get('role', 'buyer')
        status_filter = (request.args.get('status') or '').strip()
        q = (request.args.get('q') or '').strip()
        sort = (request.args.get('sort') or 'new').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 10
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        base = (
            "SELECT l.id, l.title, l.category, l.subcategory, l.price, l.status, "
            "l.approval_status, l.created_at, l.photos, l.location, l.view_count, "
            "(b.id IS NOT NULL) AS boosted, b.expiry_date AS boost_expiry "
            "FROM listings l "
            "LEFT JOIN ad_boosts b ON b.ad_id = l.id AND b.status='active' AND b.expiry_date>NOW() "
            "WHERE l.user_id=%s"
        )
        params = [user_id]
        if status_filter == 'active':
            base += " AND l.status='active'"
        elif status_filter == 'pending':
            base += " AND l.approval_status='pending'"
        elif status_filter == 'sold':
            base += " AND (l.status='sold' OR l.approval_status='sold')"
        elif status_filter == 'rejected':
            base += " AND l.approval_status='rejected'"
        elif status_filter == 'approved':
            base += " AND l.approval_status='approved'"
        if q:
            base += " AND (l.title LIKE %s OR l.category LIKE %s)"
            like_q = f"%{q}%"
            params.extend([like_q, like_q])
        order_sql = " ORDER BY l.created_at DESC"
        if sort == 'old':
            order_sql = " ORDER BY l.created_at ASC"
        elif sort == 'price_asc':
            order_sql = " ORDER BY l.price ASC"
        elif sort == 'price_desc':
            order_sql = " ORDER BY l.price DESC"
        elif sort == 'views_desc':
            order_sql = " ORDER BY l.view_count DESC"
        count_sql = "SELECT COUNT(*) as total FROM listings l WHERE l.user_id=%s"
        count_params = [user_id]
        if status_filter == 'active':
            count_sql += " AND l.status='active'"
        elif status_filter == 'pending':
            count_sql += " AND l.approval_status='pending'"
        elif status_filter == 'sold':
            count_sql += " AND (l.status='sold' OR l.approval_status='sold')"
        elif status_filter == 'rejected':
            count_sql += " AND l.approval_status='rejected'"
        elif status_filter == 'approved':
            count_sql += " AND l.approval_status='approved'"
        if q:
            count_sql += " AND (l.title LIKE %s OR l.category LIKE %s)"
            like_q2 = f"%{q}%"
            count_params.extend([like_q2, like_q2])
        cursor.execute(count_sql, count_params)
        row = cursor.fetchone()
        total = row['total'] if row else 0
        offset = (page - 1) * per_page
        base += order_sql + " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        try:
            cursor.execute(base, params)
            listings = cursor.fetchall()
        except Exception:
            cursor.execute(
                "SELECT id, title, category, subcategory, price, status, approval_status, created_at, photos "
                "FROM listings WHERE user_id=%s ORDER BY created_at DESC LIMIT %s OFFSET %s",
                [user_id, per_page, offset]
            )
            listings = cursor.fetchall()
        # Batch engagement metrics
        listing_ids = [l['id'] for l in listings] if listings else []
        fav_counts = {}
        msg_counts = {}
        exp_dates = {}
        if listing_ids:
            try:
                fmt = ','.join(['%s'] * len(listing_ids))
                cursor.execute(f"SELECT listing_id, COUNT(*) as cnt FROM favorites WHERE listing_id IN ({fmt}) GROUP BY listing_id", tuple(listing_ids))
                for r in cursor.fetchall():
                    fav_counts[r['listing_id']] = r['cnt']
            except Exception:
                fav_counts = {}
            try:
                fmt = ','.join(['%s'] * len(listing_ids))
                cursor.execute(f"""
                    SELECT c.listing_id, COUNT(m.id) as cnt
                    FROM conversations c
                    LEFT JOIN messages m ON m.conversation_id = c.id
                    WHERE c.listing_id IN ({fmt})
                    GROUP BY c.listing_id
                """, tuple(listing_ids))
                for r in cursor.fetchall():
                    msg_counts[r['listing_id']] = r['cnt']
            except Exception:
                msg_counts = {}
            try:
                fmt = ','.join(['%s'] * len(listing_ids))
                cursor.execute(f"SELECT id, expires_date FROM listings WHERE id IN ({fmt})", tuple(listing_ids))
                for r in cursor.fetchall():
                    exp_dates[r['id']] = r.get('expires_date')
            except Exception:
                exp_dates = {}
        cursor.close()
        conn.close()
        now = datetime.now()
        enriched = []
        for l in listings:
            d = dict(l)
            try:
                d['days_active'] = max(0, (now - d['created_at']).days) if d.get('created_at') else 0
            except Exception:
                d['days_active'] = 0
            d['favorites_count'] = fav_counts.get(d['id'], 0)
            d['messages_count'] = msg_counts.get(d['id'], 0)
            d['boosted'] = bool(d.get('boosted'))
            d['boost_expires'] = d.get('boost_expiry')
            # days remaining
            exp = exp_dates.get(d['id'])
            try:
                if exp:
                    d['days_remaining'] = max(0, (exp - now).days)
                else:
                    d['days_remaining'] = None
            except Exception:
                d['days_remaining'] = None
            # performance percent
            views = d.get('view_count') or 0
            favs = d['favorites_count'] or 0
            perf = min(100, int(views * 1 + favs * 5))
            d['performance_percent'] = perf
            enriched.append(d)
        total_pages = (total + per_page - 1) // per_page
        return render_template(
            "my_listings.html",
            listings=enriched,
            username=username,
            role=role,
            status_filter=status_filter,
            q=q,
            sort=sort,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        flash(f"❌ Error loading listings: {str(e)}", "error")
        return redirect(url_for("dashboard"))

@app.route("/dashboard/my-listings")
@login_required
def my_listings_alias():
    return my_listings()

@app.route("/renew/<int:product_id>", methods=["POST"])
@login_required
def renew_listing(product_id):
    """Renew listing by extending expires_date and setting status active"""
    user_id = session.get('user_id')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # ensure ownership
        cur.execute("SELECT user_id FROM listings WHERE id=%s", (product_id,))
        row = cur.fetchone()
        if not row or row[0] != user_id:
            cur.close()
            conn.close()
            flash("❌ You can only renew your own listing", "error")
            return redirect(url_for("my_listings"))
        # try update expires_date, fallback to status only
        try:
            cur.execute("UPDATE listings SET expires_date=DATE_ADD(NOW(), INTERVAL 30 DAY), status='active' WHERE id=%s", (product_id,))
        except Exception:
            cur.execute("UPDATE listings SET status='active' WHERE id=%s", (product_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("✅ Listing renewed for 30 days", "success")
    except Exception as e:
        flash(f"❌ Error renewing listing: {e}", "error")
    return redirect(url_for("my_listings"))

@app.route("/browse")
def browse():
    """Browse all listings with optional category filter"""
    try:
        # Get filter parameters
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build dynamic query based on filters
        query = """
            SELECT l.id, l.title, l.category, l.subcategory, l.price, l.location, l.created_at, l.photos, u.username,
                   CASE WHEN b.id IS NULL THEN 0 ELSE 1 END AS is_boosted,
                   b.expiry_date AS boost_expiry
            FROM listings l
            JOIN users u ON l.user_id = u.id
            LEFT JOIN ad_boosts b ON b.ad_id=l.id AND b.status='active' AND b.expiry_date>NOW()
            WHERE l.approval_status='approved' AND l.status='active'
        """
        params = []
        
        # Apply category filter if provided
        if category_filter:
            query += " AND l.category = %s"
            params.append(category_filter)
        
        # Apply search filter if provided
        if search_query:
            query += " AND (l.title LIKE %s OR l.description LIKE %s OR l.category LIKE %s)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])
        
        query += " ORDER BY is_boosted DESC, boost_expiry DESC, l.created_at DESC"
        # Try with location column; if missing, fallback selecting literal for location
        try:
            cursor.execute(query, params)
        except Exception:
            query = query.replace("l.location", "'' AS location")
            cursor.execute(query, params)
        listings = cursor.fetchall()
        
        # Get all categories for the filter dropdown
        cursor.execute("SELECT DISTINCT category FROM listings WHERE approval_status='approved' ORDER BY category")
        categories = [row['category'] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return render_template("browse_listings.html", 
                             listings=listings, 
                             categories=categories,
                             selected_category=category_filter,
                             search_query=search_query)
        
    except Exception as e:
        flash(f"❌ Error loading listings: {str(e)}", "error")
        return redirect(url_for("home"))

# ---------- Helper routines for conversations/messages ----------

def get_or_create_conversation(listing_id, buyer_id):
    """Return existing conversation id for buyer+listing, or create a new one.
    Also inserts a default first message and notifies the seller."""
    # Ensure chat tables exist before any operations
    try:
        ensure_chat_tables()
    except Exception:
        pass
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # see if conversation already exists
    cursor.execute(
        "SELECT * FROM conversations WHERE listing_id=%s AND buyer_id=%s",
        (listing_id, buyer_id)
    )
    conv = cursor.fetchone()

    if conv:
        conv_id = conv['id']
    else:
        # fetch seller from listing
        cursor.execute("SELECT user_id FROM listings WHERE id=%s", (listing_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return None
        seller_id = row['user_id']

        cursor.execute(
            "INSERT INTO conversations (listing_id, buyer_id, seller_id, created_at) VALUES (%s,%s,%s,NOW())",
            (listing_id, buyer_id, seller_id)
        )
        conv_id = cursor.lastrowid
        conn.commit()

        # default initial message from buyer
        default_msg = "Hi, I am interested in this product. Is it still available?"
        cursor.execute(
            "INSERT INTO messages (conversation_id, sender_id, content, created_at) VALUES (%s,%s,%s,NOW())",
            (conv_id, buyer_id, default_msg)
        )
        conn.commit()

        # notify seller (simple notification table)
        try:
            cursor.execute(
                "INSERT INTO notifications (user_id, message, is_read, created_at) VALUES (%s,%s,0,NOW())",
                (seller_id, "New buyer interested in your product.")
            )
            conn.commit()
        except Exception:
            # ignore; notification table may not exist yet
            pass

    cursor.close()
    conn.close()
    return conv_id


@app.route("/buy/<int:listing_id>")
@login_required
def buy_now(listing_id):
    """Entry point when user clicks Buy Now. If conversation already
    exists we open it; otherwise create a new one and redirect."""
    user_id = session.get('user_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, user_id, status FROM listings WHERE id=%s", (listing_id,))
        listing = cursor.fetchone()
        cursor.close()
        conn.close()

        if not listing:
            flash("❌ Listing not found", "error")
            return redirect(url_for("browse"))

        if listing['status'] == 'sold':
            flash("❌ This item has already been sold", "error")
            return redirect(url_for('view_listing', listing_id=listing_id))

        # buyer cannot buy their own listing
        if listing['user_id'] == user_id:
            flash("❌ You cannot start a conversation on your own listing", "error")
            return redirect(url_for('view_listing', listing_id=listing_id))

        conv_id = get_or_create_conversation(listing_id, user_id)
        if not conv_id:
            flash("❌ Could not start conversation", "error")
            return redirect(url_for('view_listing', listing_id=listing_id))

        return redirect(url_for('chat_page', conv_id=conv_id))
    except Exception as e:
        flash(f"❌ Error opening chat: {e}", "error")
        return redirect(url_for('view_listing', listing_id=listing_id))


@app.route("/chat/<int:conv_id>", methods=["GET", "POST"])
@login_required
def chat_page(conv_id):
    """Render conversation page or handle a new message post."""
    user_id = session.get('user_id')
    try:
        ensure_chat_tables()
    except Exception:
        pass

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # verify conversation exists and user is participant
    cursor.execute("SELECT * FROM conversations WHERE id=%s", (conv_id,))
    conv = cursor.fetchone()
    if not conv or user_id not in (conv['buyer_id'], conv['seller_id']):
        cursor.close()
        conn.close()
        flash("❌ Conversation not found or access denied", "error")
        return redirect(url_for('home'))

    # fetch listing details for summary card
    cursor.execute(
        "SELECT l.*, u.username as seller_name FROM listings l JOIN users u ON l.user_id=u.id WHERE l.id=%s",
        (conv['listing_id'],)
    )
    listing = cursor.fetchone()

    if request.method == 'POST':
        msg = request.form.get('message')
        if msg:
            cursor.execute(
                "INSERT INTO messages (conversation_id, sender_id, content, created_at) VALUES (%s,%s,%s,NOW())",
                (conv_id, user_id, msg)
            )
            conn.commit()
            # update last_message_at
            cursor.execute("UPDATE conversations SET last_message_at=NOW() WHERE id=%s", (conv_id,))
            conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('chat_page', conv_id=conv_id))

    # GET path: load messages
    cursor.execute(
        "SELECT m.*, u.username FROM messages m JOIN users u ON m.sender_id=u.id WHERE m.conversation_id=%s ORDER BY m.created_at ASC",
        (conv_id,)
    )
    messages = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('chat.html', conversation=conv, messages=messages, listing=listing)


@app.route("/chat/<int:conv_id>/mark_sold", methods=["POST"])
@login_required
def mark_sold(conv_id):
    user_id = session.get('user_id')
    try:
        ensure_chat_tables()
    except Exception:
        pass

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM conversations WHERE id=%s", (conv_id,))
    conv = cursor.fetchone()
    if not conv or conv['seller_id'] != user_id:
        cursor.close()
        conn.close()
        flash("❌ You are not authorized to mark this item sold", "error")
        return redirect(url_for('home'))

    # update listing status
    cursor.execute("UPDATE listings SET status='sold' WHERE id=%s", (conv['listing_id'],))
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Listing marked as sold", "success")
    return redirect(url_for('chat_page', conv_id=conv_id))


@app.route("/listing/<int:listing_id>")
def view_listing(listing_id):
    """View individual listing details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT l.*, u.username, u.phone as seller_phone, u.email as seller_email,
                   u.created_at as seller_joined, u.profile_photo as seller_photo,
                   CASE WHEN b.id IS NULL THEN 0 ELSE 1 END AS is_boosted,
                   b.expiry_date AS boost_expiry
            FROM listings l
            JOIN users u ON l.user_id = u.id
            LEFT JOIN ad_boosts b ON b.ad_id=l.id AND b.status='active' AND b.expiry_date>NOW()
            WHERE l.id=%s
        """, (listing_id,))
        
        listing = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not listing:
            flash("❌ Listing not found", "error")
            return redirect(url_for("browse"))

        # wishlist state from session
        wl = session.get('wishlist', [])
        listing['in_wishlist'] = listing_id in wl

        # add extra seller info: total active listings
        try:
            conn = get_db_connection()
            cur2 = conn.cursor()
            cur2.execute("SELECT COUNT(*) FROM listings WHERE user_id=%s AND status='active'", (listing['user_id'],))
            listing['seller_listings_count'] = cur2.fetchone()[0]
            cur2.close()
            conn.close()
        except Exception:
            listing['seller_listings_count'] = 0

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

@app.route("/product/<int:product_id>")
def product_page(product_id):
    return redirect(url_for('view_listing', listing_id=product_id))

@app.route("/promotion/<int:product_id>")
@login_required
def promotion_alias(product_id):
    return redirect(url_for('boost_listing', listing_id=product_id))

@app.route("/boost/<int:listing_id>", methods=["GET","POST"])
@login_required
def boost_listing(listing_id):
    user_id = session.get('user_id')
    try:
        try:
            ensure_boost_tables()
        except Exception:
            pass
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, user_id, title, price, photos FROM listings WHERE id=%s", (listing_id,))
        listing = cur.fetchone()
        if not listing:
            cur.close()
            conn.close()
            flash("❌ Listing not found", "error")
            return redirect(url_for("my_listings"))
        cur.execute("SELECT * FROM boost_packages ORDER BY price ASC")
        rows = cur.fetchall()
        packages = []
        for p in rows:
            key = "basic" if "basic" in (p["name"] or "").lower() else "featured" if "featured" in (p["name"] or "").lower() else "premium"
            packages.append({
                "id": p["id"],
                "key": key,
                "name": p["name"],
                "days": int(p["duration_days"] or 0),
                "price": float(p["price"] or 0.0)
            })
        cur.close()
        conn.close()
        return render_template("boost_listing.html", listing=listing, packages=packages)
    except Exception as e:
        flash(f"❌ Error loading boost options: {e}", "error")
        return redirect(url_for("my_listings"))
@app.route("/buy-boost/<int:package_id>/<int:ad_id>")
@login_required
def buy_boost(package_id, ad_id):
    user_id = session.get('user_id')
    try:
        ensure_boost_tables()
    except Exception:
        pass
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, user_id FROM listings WHERE id=%s", (ad_id,))
        listing = cur.fetchone()
        if not listing:
            cur.close()
            conn.close()
            flash("❌ Listing not found", "error")
            return redirect(url_for("my_listings"))
        if listing["user_id"] != user_id:
            cur.close()
            conn.close()
            flash("❌ You can only boost your own listing", "error")
            return redirect(url_for("my_listings"))
        cur.execute("SELECT * FROM boost_packages WHERE id=%s", (package_id,))
        pkg = cur.fetchone()
        if not pkg:
            cur.close()
            conn.close()
            flash("❌ Package not found", "error")
            return redirect(url_for("boost_listing", listing_id=ad_id))
        cur.execute(
            "INSERT INTO payments (user_id, ad_id, amount, method, status, created_at) VALUES (%s,%s,%s,%s,%s,NOW())",
            (user_id, ad_id, float(pkg["price"]), "upi", "paid")
        )
        payment_id = cur.lastrowid
        cur.execute(
            "INSERT INTO ad_boosts (user_id, ad_id, package_id, payment_id, start_date, expiry_date, status, created_at) VALUES (%s,%s,%s,%s,NOW(), DATE_ADD(NOW(), INTERVAL %s DAY), 'active', NOW())",
            (user_id, ad_id, pkg["id"], payment_id, int(pkg["duration_days"]))
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("payment_success"))
    except Exception as e:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
        flash(f"❌ Error purchasing boost: {e}", "error")
        return redirect(url_for("boost_listing", listing_id=ad_id))
@app.route("/boost-ad/<int:ad_id>", methods=["GET","POST"])
@login_required
def boost_ad_alias(ad_id):
    return boost_listing(ad_id)
@app.route("/checkout/<int:package_id>/<int:ad_id>", methods=["GET","POST"])
@login_required
def checkout(package_id, ad_id):
    user_id = session.get('user_id')
    try:
        ensure_boost_tables()
    except Exception:
        pass
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, user_id, title, price FROM listings WHERE id=%s", (ad_id,))
        ad = cur.fetchone()
        cur.execute("SELECT * FROM boost_packages WHERE id=%s", (package_id,))
        pkg = cur.fetchone()
        if not ad or not pkg:
            cur.close()
            conn.close()
            flash("❌ Invalid ad or package", "error")
            return redirect(url_for("my_listings"))
        if ad["user_id"] != user_id:
            cur.close()
            conn.close()
            flash("❌ You can only boost your own ad", "error")
            return redirect(url_for("my_listings"))
        if request.method == "POST":
            method = (request.form.get("payment_method") or "upi").lower()
            txid = secrets.token_hex(8)
            cur.execute("""
                INSERT INTO payments (user_id, ad_id, package_id, amount, method, transaction_id, status, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,'success',NOW())
            """, (user_id, ad_id, pkg["id"], float(pkg["price"]), method, txid))
            payment_id = cur.lastrowid
            cur.execute("""
                INSERT INTO ad_boosts (user_id, ad_id, package_id, payment_id, start_date, expiry_date, status, created_at)
                VALUES (%s,%s,%s,%s,NOW(), DATE_ADD(NOW(), INTERVAL %s DAY), 'active', NOW())
            """, (user_id, ad_id, pkg["id"], payment_id, int(pkg["duration_days"])))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("payment_success"))
        cur.close()
        conn.close()
        return render_template("checkout_boost.html", ad=ad, pkg=pkg)
    except Exception as e:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
        flash(f"❌ Error during checkout: {e}", "error")
        return redirect(url_for("boost_listing", listing_id=ad_id))
@app.route("/payment-success")
@login_required
def payment_success():
    flash("✅ Payment successful. Boost activated!", "success")
    return redirect(url_for("my_promotions"))
@app.route("/my-promotions")
@login_required
def my_promotions():
    user_id = session.get('user_id')
    active = []
    history = []
    payments = []
    insights = []
    try:
        ensure_boost_tables()
    except Exception:
        pass
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT b.id, b.ad_id, b.package_id, b.start_date, b.expiry_date, b.status,
                   l.title as listing_title, l.photos, p.name as package_name,
                   pay.amount, pay.method as payment_method, pay.transaction_id
            FROM ad_boosts b
            LEFT JOIN listings l ON b.ad_id=l.id
            LEFT JOIN boost_packages p ON p.id=b.package_id
            LEFT JOIN payments pay ON pay.id=b.payment_id
            WHERE b.user_id=%s AND b.status='active' AND b.expiry_date>NOW()
            ORDER BY b.start_date DESC
        """, (user_id,))
        active = cur.fetchall()
        cur.execute("""
            SELECT b.id, b.ad_id, b.package_id, b.start_date, b.expiry_date, b.status,
                   l.title as listing_title, p.name as package_name, pay.amount, pay.method as payment_method, pay.transaction_id
            FROM ad_boosts b
            LEFT JOIN listings l ON b.ad_id=l.id
            LEFT JOIN boost_packages p ON p.id=b.package_id
            LEFT JOIN payments pay ON pay.id=b.payment_id
            WHERE b.user_id=%s
            ORDER BY b.start_date DESC
        """, (user_id,))
        rows = cur.fetchall()
        now = datetime.now()
        for r in rows:
            st = r["status"]
            if not r["listing_title"]:
                st = "listing_deleted"
            elif r["expiry_date"] and r["expiry_date"] < now:
                st = "expired"
            if r not in active:
                rec = dict(r)
                rec["resolved_status"] = st
                history.append(rec)
        cur.execute("""
            SELECT pay.id, pay.amount, pay.method as payment_method, pay.transaction_id, pay.status as payment_status, pay.created_at,
                   l.title as listing_title, bp.name as package_name
            FROM payments pay
            LEFT JOIN listings l ON pay.ad_id=l.id
            LEFT JOIN boost_packages bp ON pay.package_id=bp.id
            WHERE pay.user_id=%s
            ORDER BY pay.created_at DESC
        """, (user_id,))
        payments = cur.fetchall()
        if active:
            ad_ids = [a["ad_id"] for a in active if a.get("ad_id")]
            if ad_ids:
                fmt = ",".join(["%s"] * len(ad_ids))
                fav_counts = {}
                msg_counts = {}
                views_map = {}
                cur.execute(f"SELECT id, view_count FROM listings WHERE id IN ({fmt})", tuple(ad_ids))
                for r in cur.fetchall():
                    views_map[r["id"]] = int(r.get("view_count") or 0)
                try:
                    cur.execute(f"""
                        SELECT listing_id, COUNT(*) as c
                        FROM favorites
                        WHERE listing_id IN ({fmt})
                        GROUP BY listing_id
                    """, tuple(ad_ids))
                    for r in cur.fetchall():
                        fav_counts[r["listing_id"]] = int(r["c"])
                except Exception:
                    pass
                try:
                    cur.execute(f"""
                        SELECT c.listing_id, COUNT(m.id) as c
                        FROM conversations c
                        LEFT JOIN messages m ON c.id=m.conversation_id
                        WHERE c.listing_id IN ({fmt})
                        GROUP BY c.listing_id
                    """, tuple(ad_ids))
                    for r in cur.fetchall():
                        msg_counts[r["listing_id"]] = int(r["c"])
                except Exception:
                    pass
                for a in active:
                    adid = a.get("ad_id")
                    dur = 0
                    try:
                        if a.get("start_date") and a.get("expiry_date"):
                            dur = (a["expiry_date"] - a["start_date"]).days
                    except Exception:
                        dur = 0
                    insights.append({
                        "ad_id": adid,
                        "title": a.get("listing_title") or "Deleted Listing",
                        "views": views_map.get(adid, 0),
                        "clicks": fav_counts.get(adid, 0),
                        "messages": msg_counts.get(adid, 0),
                        "duration_days": dur
                    })
        cur.close()
        conn.close()
    except Exception:
        active, history, payments, insights = [], [], [], []
    return render_template("my_promotions.html", active=active, history=history, payments=payments, insights=insights)

@app.route("/invoice/<int:payment_id>")
@login_required
def invoice_download(payment_id):
    user_id = session.get('user_id')
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT pay.id, pay.user_id, pay.amount, pay.method, pay.transaction_id, pay.created_at, pay.status,
                   u.username as user_name, l.title as listing_title, bp.name as package_name
            FROM payments pay
            JOIN users u ON u.id=pay.user_id
            LEFT JOIN listings l ON l.id=pay.ad_id
            LEFT JOIN boost_packages bp ON bp.id=pay.package_id
            WHERE pay.id=%s
        """, (payment_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row or row["user_id"] != user_id:
            flash("❌ Access denied", "error")
            return redirect(url_for("my_promotions"))
        html = f"""
        <html><head><meta charset="utf-8"><title>Invoice #{row['id']}</title></head>
        <body style="font-family:Arial, sans-serif; padding:24px;">
          <h2>ReGear Invoice</h2>
          <p><strong>Invoice ID:</strong> {row['id']}</p>
          <p><strong>User Name:</strong> {row.get('user_name','')}</p>
          <p><strong>Product:</strong> {row.get('listing_title') or 'Deleted Listing'}</p>
          <p><strong>Boost Plan:</strong> {row.get('package_name') or 'N/A'}</p>
          <p><strong>Amount Paid:</strong> ₹{int(row['amount'] or 0)}</p>
          <p><strong>Payment Method:</strong> {row.get('method','')}</p>
          <p><strong>Transaction ID:</strong> {row.get('transaction_id') or 'N/A'}</p>
          <p><strong>Date:</strong> {row['created_at']}</p>
          <p><strong>Status:</strong> {row.get('status','')}</p>
          <hr/>
          <small>Thank you for using ReGear.</small>
        </body></html>
        """
        from flask import make_response
        resp = make_response(html)
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
        resp.headers["Content-Disposition"] = f"attachment; filename=invoice-{row['id']}.html"
        return resp
    except Exception:
        flash("❌ Could not generate invoice", "error")
        return redirect(url_for("my_promotions"))

@app.route("/mark-sold/<int:product_id>")
@login_required
def mark_sold_quick(product_id):
    user_id = session.get('user_id')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE listings SET status='sold' WHERE id=%s AND user_id=%s", (product_id, user_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("✅ Listing marked as sold", "success")
    except Exception as e:
        flash(f"❌ Error marking as sold: {e}", "error")
    return redirect(url_for("my_listings"))

@app.route("/delete-product/<int:product_id>")
@login_required
def delete_product(product_id):
    user_id = session.get('user_id')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM listings WHERE id=%s AND user_id=%s", (product_id, user_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("✅ Listing deleted", "success")
    except Exception as e:
        flash(f"❌ Error deleting listing: {e}", "error")
    return redirect(url_for("my_listings"))

@app.route("/edit-product/<int:product_id>", methods=["GET","POST"])
@login_required
def edit_product(product_id):
    user_id = session.get('user_id')
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        if request.method == "POST":
            title = request.form.get('title') or ''
            price = request.form.get('price') or ''
            description = request.form.get('description') or ''
            location = request.form.get('location') or ''
            condition = request.form.get('condition') or ''
            cur.execute("""
                UPDATE listings SET title=%s, price=%s, description=%s, location=%s, item_condition=%s
                WHERE id=%s AND user_id=%s
            """, (title, price, description, location, condition, product_id, user_id))
            conn.commit()
            cur.close()
            conn.close()
            flash("✅ Listing updated", "success")
            return redirect(url_for('product_page', product_id=product_id))
        cur.execute("SELECT * FROM listings WHERE id=%s AND user_id=%s", (product_id, user_id))
        listing = cur.fetchone()
        cur.close()
        conn.close()
        if not listing:
            flash("❌ Access denied or listing not found", "error")
            return redirect(url_for('my_listings'))
        return render_template("edit_product.html", listing=listing)
    except Exception as e:
        flash(f"❌ Error editing listing: {e}", "error")
        return redirect(url_for("my_listings"))

@app.route("/wishlist/toggle/<int:listing_id>")
@login_required

def toggle_wishlist(listing_id):
    """Add or remove a listing from the user's wishlist stored in session"""
    user_id = session.get('user_id')
    wl = session.get('wishlist', [])
    added = False
    # Session toggle
    if listing_id in wl:
        wl.remove(listing_id)
    else:
        wl.append(listing_id)
        added = True
    session['wishlist'] = wl
    # DB-backed favorites (create table if needed)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                listing_id INT NOT NULL,
                created_at DATETIME NOT NULL,
                UNIQUE KEY uniq_fav (user_id, listing_id),
                INDEX idx_user (user_id),
                INDEX idx_listing (listing_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        if added:
            cur.execute("INSERT IGNORE INTO favorites (user_id, listing_id, created_at) VALUES (%s, %s, NOW())", (user_id, listing_id))
        else:
            cur.execute("DELETE FROM favorites WHERE user_id=%s AND listing_id=%s", (user_id, listing_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
    action = 'added' if added else 'removed'
    flash(f"✅ Wishlist {action}", "success")
    return redirect(url_for('view_listing', listing_id=listing_id))


@app.route("/api/wishlist")
@login_required

def api_wishlist():
    """Return JSON array of wishlisted listings for current session"""
    wl = session.get('wishlist', [])
    result = []
    if wl:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            format_ids = ','.join(['%s'] * len(wl))
            query = f"SELECT id, title, price, photos FROM listings WHERE id IN ({format_ids}) AND status='active'"
            cursor.execute(query, tuple(wl))
            rows = cursor.fetchall()
            for r in rows:
                main_img = r['photos'].split(',')[0] if r.get('photos') else ''
                result.append({
                    'id': r['id'],
                    'title': r['title'],
                    'price': r['price'],
                    'img': main_img
                })
            cursor.close()
            conn.close()
        except Exception:
            pass
    return jsonify(result)


@app.context_processor
def inject_wishlist_count():
    wl = session.get('wishlist', [])
    is_auth = 'user_id' in session
    display_username = session.get('username', 'User')
    user_initial = display_username[:1].upper() if display_username else 'U'
    current_user = None
    if is_auth:
        try:
            # prefer session value for immediate updates without extra DB hit
            photo = session.get('profile_photo')
            name = display_username
            if not photo or not name:
                conn = get_db_connection()
                cur = conn.cursor(dictionary=True)
                try:
                    # prefer profile_photo; fallback to older profile_image
                    cur.execute("SELECT username, full_name, profile_photo, profile_image FROM users WHERE id=%s", (session.get('user_id'),))
                    row = cur.fetchone()
                except Exception:
                    try:
                        cur.execute("SELECT username, full_name, profile_image FROM users WHERE id=%s", (session.get('user_id'),))
                        row = cur.fetchone()
                    except Exception:
                        row = None
                cur.close()
                conn.close()
                if row:
                    name = row.get('full_name') or row.get('username') or display_username
                    photo = row.get('profile_photo') or row.get('profile_image')
            display_username = name or display_username
            user_initial = (name[:1].upper() if name else user_initial)
            current_user = {'name': display_username, 'photo': photo}
        except Exception:
            current_user = {'name': display_username, 'photo': None}
    return {'wishlist_count': len(wl), 'username': display_username, 'role': session.get('role', 'buyer'), 'is_authenticated': is_auth, 'user_initial': user_initial, 'current_user': current_user}

@app.route("/help")
def help_page():
    flash("For help, contact support via Messages", "info")
    return redirect(url_for("messages_list") if 'user_id' in session else url_for("login"))

@app.route("/settings")
@login_required
def settings():
    return redirect(url_for("profile"))

@app.template_filter('imgurl')
def imgurl(path):
    try:
        from flask import url_for
        if not path:
            return ''
        p = str(path).strip().lstrip('/\\')
        if p.lower().startswith('static/'):
            p = p[7:]
        return url_for('static', filename=p)
    except Exception:
        return ''

def ensure_chat_tables():
    """Create conversations/messages tables if they don't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                listing_id INT NOT NULL,
                buyer_id INT NOT NULL,
                seller_id INT NOT NULL,
                created_at DATETIME NOT NULL,
                last_message_at DATETIME NULL,
                INDEX idx_listing (listing_id),
                INDEX idx_participants (buyer_id, seller_id),
                INDEX idx_last_message (last_message_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NOT NULL,
                sender_id INT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                INDEX idx_conv (conversation_id),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    finally:
        cur.close()
        conn.close()
def ensure_boost_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS boost_packages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                duration_days INT NOT NULL,
                boost_type VARCHAR(50) NOT NULL,
                description VARCHAR(255) DEFAULT NULL,
                UNIQUE KEY uniq_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ad_boosts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                ad_id INT NOT NULL,
                package_id INT NOT NULL,
                payment_id INT DEFAULT NULL,
                start_date DATETIME NOT NULL,
                expiry_date DATETIME NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                created_at DATETIME NOT NULL,
                INDEX idx_ad (ad_id),
                INDEX idx_user (user_id),
                INDEX idx_expiry (expiry_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                ad_id INT DEFAULT NULL,
                package_id INT DEFAULT NULL,
                amount DECIMAL(10,2) NOT NULL,
                method VARCHAR(30) NOT NULL,
                transaction_id VARCHAR(64) DEFAULT NULL,
                status VARCHAR(20) NOT NULL,
                created_at DATETIME NOT NULL,
                INDEX idx_user (user_id),
                INDEX idx_ad (ad_id),
                INDEX idx_pkg (package_id),
                INDEX idx_status (status),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        try:
            cur.execute("ALTER TABLE payments ADD COLUMN package_id INT DEFAULT NULL")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE payments ADD COLUMN transaction_id VARCHAR(64) DEFAULT NULL")
        except Exception:
            pass
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM boost_packages")
        cnt = cur.fetchone()[0]
        if cnt == 0:
            cur.executemany(
                "INSERT INTO boost_packages (name, price, duration_days, boost_type, description) VALUES (%s,%s,%s,%s,%s)",
                [
                    ("Basic Boost", 49, 3, "top_category", "Top of category results"),
                    ("Featured Boost", 99, 5, "homepage_featured", "Featured on homepage"),
                    ("Premium Boost", 199, 7, "premium", "Top ranking + featured badge")
                ]
            )
            conn.commit()
    finally:
        cur.close()
        conn.close()
@app.route("/tasks/expire-listings")
def task_expire_listings():
    """Mark listings expired when free trial or boost expires.
    Safe to call manually or via scheduler."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE listings
            SET status='expired'
            WHERE (expires_date IS NOT NULL AND expires_date < NOW())
              AND (status='active' OR status IS NULL)
              AND (COALESCE(is_sold, 0)=0)
        """)
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "expired": affected})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
@app.route("/tasks/expire-boosts")
def task_expire_boosts():
    try:
        ensure_boost_tables()
    except Exception:
        pass
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE ad_boosts
            SET status='expired'
            WHERE expiry_date<NOW() AND status='active'
        """)
        affected = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "expired": affected})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/favorites")
@login_required
def favorites():
    """Render wishlist grid from session."""
    user_id = session.get('user_id')
    items = []
    # Prefer DB favorites if available
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT l.id, l.title, l.price, l.photos, l.location
                FROM favorites f
                JOIN listings l ON f.listing_id = l.id
                WHERE f.user_id=%s
                ORDER BY f.created_at DESC
            """, (user_id,))
        except Exception:
            cur.execute("""
                SELECT l.id, l.title, l.price, l.photos, '' AS location
                FROM favorites f
                JOIN listings l ON f.listing_id = l.id
                WHERE f.user_id=%s
                ORDER BY f.created_at DESC
            """, (user_id,))
        items = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        # Fallback to session-based wishlist
        wl = session.get('wishlist', [])
        if wl:
            try:
                conn = get_db_connection()
                cur = conn.cursor(dictionary=True)
                format_ids = ','.join(['%s'] * len(wl))
                try:
                    cur.execute(f"SELECT id, title, price, photos, location FROM listings WHERE id IN ({format_ids}) AND status IN ('active','sold')", tuple(wl))
                except Exception:
                    cur.execute(f"SELECT id, title, price, photos, '' AS location FROM listings WHERE id IN ({format_ids}) AND status IN ('active','sold')", tuple(wl))
                items = cur.fetchall()
                cur.close()
                conn.close()
            except Exception:
                items = []
    return render_template("favorites.html", items=items)

@app.route("/messages")
@login_required
def messages_list():
    """List conversations for current user."""
    try:
        ensure_chat_tables()
    except Exception:
        pass
    user_id = session.get('user_id')
    convs = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT c.id, c.listing_id, c.buyer_id, c.seller_id, c.last_message_at
            FROM conversations c
            WHERE c.buyer_id=%s OR c.seller_id=%s
            ORDER BY COALESCE(c.last_message_at, c.created_at) DESC
        """, (user_id, user_id))
        rows = cur.fetchall()
        for r in rows:
            # last message
            try:
                cur.execute("SELECT content, created_at FROM messages WHERE conversation_id=%s ORDER BY created_at DESC LIMIT 1", (r['id'],))
                m = cur.fetchone()
                last_message = m['content'] if m else None
                last_time = m['created_at'] if m else r.get('last_message_at')
            except Exception:
                last_message, last_time = None, None
            # product title
            try:
                cur.execute("SELECT title FROM listings WHERE id=%s", (r['listing_id'],))
                pt = cur.fetchone()
                product_title = pt['title'] if pt else f"Listing #{r['listing_id']}"
            except Exception:
                product_title = f"Listing #{r['listing_id']}"
            # other user name
            other_id = r['seller_id'] if r['buyer_id'] == user_id else r['buyer_id']
            try:
                cur.execute("SELECT username FROM users WHERE id=%s", (other_id,))
                ou = cur.fetchone()
                other_user = ou['username'] if ou else f"User #{other_id}"
            except Exception:
                other_user = f"User #{other_id}"
            convs.append({"id": r['id'], "product_title": product_title, "other_user": other_user, "last_message": last_message, "last_time": last_time})
        cur.close()
        conn.close()
    except Exception:
        convs = []
    return render_template("messages.html", convs=convs)

@app.route("/profile", methods=["GET","POST"])
@login_required
def profile():
    user_id = session.get('user_id')
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("ALTER TABLE users ADD COLUMN profile_photo VARCHAR(255)")
            conn.commit()
        except Exception:
            pass
        if request.method == "POST":
            username = (request.form.get('username') or '').strip()
            phone = (request.form.get('phone') or '').strip()
            location = (request.form.get('location') or '').strip()
            new_password = request.form.get('new_password') or ''
            remove_photo = request.form.get('remove_photo') or ''
            photo_file = request.files.get('profile_photo')
            # read existing for delete-on-replace
            existing_photo = None
            try:
                cur.execute("SELECT profile_photo FROM users WHERE id=%s", (user_id,))
                row = cur.fetchone()
                if row:
                    existing_photo = row.get('profile_photo')
            except Exception:
                existing_photo = None
            if username:
                try:
                    cur.execute("UPDATE users SET username=%s WHERE id=%s", (username, user_id))
                    session['username'] = username
                except Exception:
                    pass
            try:
                cur.execute("UPDATE users SET phone=%s WHERE id=%s", (phone, user_id))
            except Exception:
                pass
            try:
                cur.execute("ALTER TABLE users ADD COLUMN location VARCHAR(255)")
            except Exception:
                pass
            try:
                cur.execute("UPDATE users SET location=%s WHERE id=%s", (location, user_id))
            except Exception:
                pass
            # Handle remove photo
            if remove_photo == '1' and existing_photo:
                try:
                    abs_path = os.path.join(app.root_path, existing_photo.replace('/', os.sep))
                    if os.path.isfile(abs_path):
                        os.remove(abs_path)
                except Exception:
                    pass
                try:
                    cur.execute("UPDATE users SET profile_photo=NULL WHERE id=%s", (user_id,))
                except Exception:
                    pass
                session['profile_photo'] = None
            # Handle upload
            if photo_file and photo_file.filename:
                try:
                    allowed = {'jpg','jpeg','png'}
                    ext = photo_file.filename.rsplit('.',1)[-1].lower() if '.' in photo_file.filename else ''
                    if ext not in allowed:
                        flash("❌ Only JPG, JPEG, PNG allowed", "error")
                    else:
                        # size check (5MB)
                        photo_file.stream.seek(0, os.SEEK_END)
                        size = photo_file.stream.tell()
                        photo_file.stream.seek(0)
                        if size > 5 * 1024 * 1024:
                            flash("❌ File too large (max 5MB)", "error")
                        else:
                            upload_dir = os.path.join(app.root_path, 'static', 'profile_photos')
                            os.makedirs(upload_dir, exist_ok=True)
                            ts = int(datetime.now().timestamp())
                            filename = f"{user_id}_{ts}.{ext}"
                            dest = os.path.join(upload_dir, filename)
                            # resize if large
                            resized = False
                            try:
                                from PIL import Image
                                img = Image.open(photo_file.stream)
                                img = img.convert('RGB') if ext in ['jpg','jpeg'] else img.convert('RGBA')
                                max_dim = 600
                                img.thumbnail((max_dim, max_dim))
                                img.save(dest, quality=85)
                                resized = True
                            except Exception:
                                photo_file.save(dest)
                            # delete old file
                            if existing_photo:
                                try:
                                    old_abs = os.path.join(app.root_path, existing_photo.replace('/', os.sep))
                                    if os.path.isfile(old_abs):
                                        os.remove(old_abs)
                                except Exception:
                                    pass
                            rel_path = os.path.join('static','profile_photos', filename).replace('\\','/')
                            try:
                                cur.execute("UPDATE users SET profile_photo=%s WHERE id=%s", (rel_path, user_id))
                            except Exception:
                                pass
                            session['profile_photo'] = rel_path
                except Exception as _e:
                    flash("❌ Upload failed", "error")
            if new_password and len(new_password) >= 6:
                try:
                    cur.execute("UPDATE users SET password=%s WHERE id=%s", (hash_password(new_password), user_id))
                except Exception:
                    pass
            conn.commit()
            flash("✅ Profile updated", "success")
        try:
            cur.execute("SELECT id, username, email, phone, created_at, COALESCE(location, '') as location, COALESCE(profile_photo,'') as profile_photo FROM users WHERE id=%s", (user_id,))
            user = cur.fetchone()
        except Exception:
            cur.execute("SELECT id, username, email, phone, created_at FROM users WHERE id=%s", (user_id,))
            user = cur.fetchone()
            if user and isinstance(user, dict):
                user['location'] = ''
        cur.close()
        conn.close()
        return render_template("profile.html", user=user)
    except Exception as e:
        flash(f"❌ Error: {e}", "error")
        return redirect(url_for('dashboard'))

@app.route("/payments")
@login_required
def payments():
    return redirect(url_for("my_promotions"))

@app.route("/seller/<int:user_id>")
def seller_profile(user_id):
    """Display public seller profile and their listings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, created_at, role, phone, email, profile_photo FROM users WHERE id=%s", (user_id,))
        seller = cursor.fetchone()
        if not seller:
            cursor.close()
            conn.close()
            flash("❌ Seller not found", "error")
            return redirect(url_for("browse"))

        # count active listings
        cursor.execute("SELECT COUNT(*) as cnt FROM listings WHERE user_id=%s AND status='active'", (user_id,))
        seller['active_listings'] = cursor.fetchone()['cnt']
        # placeholder follower/following
        seller['followers'] = 0
        seller['following'] = 0

        # fetch seller's active listings
        cursor.execute("SELECT * FROM listings WHERE user_id=%s AND status='active' ORDER BY created_at DESC", (user_id,))
        listings = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('seller_profile.html', seller=seller, listings=listings)
    except Exception as e:
        flash(f"❌ Error loading seller profile: {e}", "error")
        return redirect(url_for('browse'))

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

        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

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

@app.route('/transactions')
@admin_required
def transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch boost payments
    cursor.execute("SELECT SUM(amount) AS boost_payments FROM transactions WHERE type = 'boost'")
    boost_payments = cursor.fetchone()['boost_payments'] or 0

    # Fetch featured listing payments
    cursor.execute("SELECT SUM(amount) AS featured_payments FROM transactions WHERE type = 'featured'")
    featured_payments = cursor.fetchone()['featured_payments'] or 0

    # Fetch subscription payments
    cursor.execute("SELECT SUM(amount) AS subscription_payments FROM transactions WHERE type = 'subscription'")
    subscription_payments = cursor.fetchone()['subscription_payments'] or 0

    # Fetch pending complaints
    cursor.execute("SELECT COUNT(*) AS pending_complaints FROM complaints WHERE status = 'pending'")
    pending_complaints = cursor.fetchone()['pending_complaints'] or 0

    # Fetch revenue by day
    cursor.execute("SELECT DATE(created_at) AS date, SUM(amount) AS daily_revenue FROM transactions GROUP BY DATE(created_at)")
    revenue_by_day = cursor.fetchall()

    # Fetch revenue by category
    cursor.execute("SELECT category, SUM(amount) AS category_revenue FROM transactions JOIN listings ON transactions.listing_id = listings.id GROUP BY category")
    revenue_by_category = cursor.fetchall()

    # Fetch top paying sellers
    cursor.execute("SELECT users.username, SUM(transactions.amount) AS total_revenue FROM transactions JOIN users ON transactions.user_id = users.id GROUP BY users.username ORDER BY total_revenue DESC LIMIT 5")
    top_paying_sellers = cursor.fetchall()

    cursor.close()
    conn.close()

    stats = {
        'boost_payments': boost_payments,
        'featured_payments': featured_payments,
        'subscription_payments': subscription_payments,
        'pending_complaints': pending_complaints
    }

    return render_template('transactions.html', stats=stats, revenue_by_day=revenue_by_day, revenue_by_category=revenue_by_category, top_paying_sellers=top_paying_sellers)

if __name__ == "__main__":
    import sys
    import io
    # Fix Unicode encoding for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    print("🚀 Starting ReGear Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📝 Register: http://localhost:5000/register")
    print("🔐 Login: http://localhost:5000/login")
    print("🛍️ Sell: http://localhost:5000/sell")
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
