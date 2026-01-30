from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import mysql.connector
from mysql.connector import Error as MySQLError
import hashlib
from functools import wraps
from datetime import datetime
import secrets

app = Flask(__name__, template_folder='templates')
app.secret_key = "regear_secret_key_secure"
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

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
try:
  def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    
    )
    print("✅ Database connected successfully!")
except MySQLError as e:
    print(f"❌ Database connection failed: {e}")
    db = None

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first!", "error")
            return redirect(url_for("login"))
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


@app.route("/")
def home():
    return render_template("homepg.html")


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
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Shra@0303",
                database="regear_db"
            )

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

            if verify_password(db_password, password):

                session["user_id"] = user_id
                session["role"] = role
                session["username"] = username

                flash("✅ Login successful", "success")

                # 🔥 ROLE BASED REDIRECT
                if role == "admin":
                    return redirect(url_for("dashboard"))
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

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="regear_db"
        )
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (new_password, session["reset_email"])
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
        "database": "connected" if db else "disconnected"
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

# Placeholder routes for dashboard features
@app.route("/browse")
@login_required
def browse():
    """Browse items"""
    flash("Browse items page coming soon!", "info")
    return redirect(url_for("dashboard"))

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
    """Post new item (for sellers)"""
    flash("Post item page coming soon!", "info")
    return redirect(url_for("dashboard"))

@app.route("/my-listings")
@login_required
def my_listings():
    """View my listings (for sellers)"""
    flash("My listings page coming soon!", "info")
    return redirect(url_for("dashboard"))

@app.route("/analytics")
@login_required
def analytics():
    """View sales analytics (for sellers)"""
    flash("Analytics page coming soon!", "info")
    return redirect(url_for("dashboard"))

@app.route("/sell")
def sell():
    return render_template("sell_electronics.html")
# ==========================
# ADMIN PANEL ROUTES
# ==========================

@app.route("/admin")
@admin_required
def admin_dashboard():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as buyers FROM users WHERE role='buyer'")
    buyers = cursor.fetchone()["buyers"]

    cursor.execute("SELECT COUNT(*) as sellers FROM users WHERE role='seller'")
    sellers = cursor.fetchone()["sellers"]

    cursor.close()

    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        buyers=buyers,
        sellers=sellers
    )


@app.route("/admin/users")
@admin_required
def admin_users():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role, created_at FROM users")
    users = cursor.fetchall()
    cursor.close()

    return render_template("admin/admin_users.html", users=users)


@app.route("/admin/block/<int:user_id>")
@admin_required
def block_user(user_id):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET role='blocked' WHERE id=%s", (user_id,))
    cursor.close()
    flash("User blocked successfully", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/unblock/<int:user_id>")
@admin_required
def unblock_user(user_id):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET role='buyer' WHERE id=%s", (user_id,))
    cursor.close()
    flash("User unblocked successfully", "success")
    return redirect(url_for("admin_users"))




# Error handlers
@app.errorhandler(404)
def not_found(error):
    return redirect(url_for("home"))

@app.errorhandler(500)
def server_error(error):
    flash("❌ Server error! Please try again.", "error")
    return redirect(url_for("home"))

if __name__ == "__main__":
    print("🚀 Starting ReGear Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📝 Register: http://localhost:5000/register")
    print("🔐 Login: http://localhost:5000/login")
    app.run(debug=True, host='localhost', port=5000)