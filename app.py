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
        
        # Fetch recent approved listings (latest 12)
        cursor.execute("""
            SELECT l.id, l.title, l.category, l.subcategory, l.price, l.location, l.created_at, l.photos, u.username
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
        role = request.form.get("role", "buyer")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        # additional seller fields
        seller_package = None
        registration_fee = None
        if role == "seller":
            # normalize package value coming from the form
            seller_package = request.form.get("package")
            if seller_package:
                seller_package = seller_package.strip()
            # validate package selection
            if not seller_package or str(seller_package) not in PACKAGE_FEES:
                flash("❌ Please select a valid seller package", "error")
                return redirect(url_for("register"))
            # store fee as numeric
            registration_fee = float(PACKAGE_FEES.get(str(seller_package)))

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
                INSERT INTO users (role, username, email, password, phone, created_at, seller_package, registration_fee)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                role, username, email, hashed_password, phone, datetime.now(),
                seller_package, registration_fee
            ))

            conn.commit()
            cursor.close()
            conn.close()

            flash("✅ Registration successful. Please login.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for("register"))

    # send package mapping for sellers so template can build options
    return render_template("register.html", package_fees=PACKAGE_FEES)


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
        "TVs & Home Entertainment": create_svg_placeholder("📺 TVs & Home", "#22543d"),
        "Gaming Consoles": "/static/images/gaming console.png",  # user image for gaming consoles
        "Speakers & Headphones": create_svg_placeholder("🔊 Audio", "#6b2c2c"),
        "Computer Accessories": "/static/images/computer accessories.png",  # User's computer accessories image
        # if user supplies a custom image, serve the file; otherwise fall back to SVG placeholder
        "Electronic Components": "/static/images/electronic component.jpg",  # custom image placed by user
        "Tablets": create_svg_placeholder("📱 Tablets", "#c53030"),
        "Smart Watches": create_svg_placeholder("⌚ Watches", "#97266d"),
        "Printers & Scanners": create_svg_placeholder("🖨️ Printers", "#2d3748"),
        "Monitors & Displays": "/static/images/Monitors & Displays.webp",  # custom monitors image
        "Smart Home Devices": create_svg_placeholder("🏠 Smart Home", "#354e78"),
        "Networking Devices": create_svg_placeholder("🌐 Network", "#6b3517"),
        "Storage Devices": create_svg_placeholder("💾 Storage", "#c53b3b")
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
            """, (user_id, category, subcategory, title, description, price, location, phone, email, condition, photos_str, datetime.now(), 'active', 'pending'))

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
    """View my listings (for sellers)"""
    try:
        user_id = session.get('user_id')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, title, category, subcategory, price, status, approval_status, created_at, photos
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
    """Browse all listings with optional category filter"""
    try:
        # Get filter parameters
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build dynamic query based on filters
        query = """
            SELECT l.id, l.title, l.category, l.subcategory, l.price, l.location, l.created_at, l.photos, u.username
            FROM listings l
            JOIN users u ON l.user_id = u.id
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
        
        query += " ORDER BY l.created_at DESC"
        
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
                   u.created_at as seller_joined
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

@app.route("/wishlist/toggle/<int:listing_id>")
@login_required

def toggle_wishlist(listing_id):
    """Add or remove a listing from the user's wishlist stored in session"""
    wl = session.get('wishlist', [])
    if listing_id in wl:
        wl.remove(listing_id)
        action = 'removed'
    else:
        wl.append(listing_id)
        action = 'added'
    session['wishlist'] = wl
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
    return {'wishlist_count': len(wl)}


@app.route("/seller/<int:user_id>")
def seller_profile(user_id):
    """Display public seller profile and their listings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, created_at, role, phone, email FROM users WHERE id=%s", (user_id,))
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

    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    print("🚀 Starting ReGear Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📝 Register: http://localhost:5000/register")
    print("🔐 Login: http://localhost:5000/login")
    print("🛍️ Sell: http://localhost:5000/sell")
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)