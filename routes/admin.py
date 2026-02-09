"""
Admin Routes - Complete Admin Dashboard Backend
Handles all admin functionality: users, products, complaints, analytics
"""

from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify
import mysql.connector
from datetime import datetime, timedelta
import json

# Admin Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("❌ Admin access required!", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated

def log_admin_action(admin_id, action, description, table_affected=None, record_id=None):
    """Log admin actions for audit trail"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, description, table_affected, record_id, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (admin_id, action, description, table_affected, record_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error logging admin action: {e}")

# ==============================
# DASHBOARD ROUTES
# ==============================

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Main admin dashboard with statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get dashboard statistics
        stats = {}

        # Total Users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role != 'admin'")
        stats['total_users'] = cursor.fetchone()['count']

        # Active users (logged in today)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM activity_logs 
            WHERE DATE(created_at) = CURDATE()
        """)
        stats['active_users'] = cursor.fetchone()['count'] or 0

        # Blocked users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='blocked'")
        stats['blocked_users'] = cursor.fetchone()['count']

        # Total listings
        cursor.execute("SELECT COUNT(*) as count FROM listings")
        stats['total_listings'] = cursor.fetchone()['count']

        # Pending approval
        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE approval_status='pending'")
        stats['pending_listings'] = cursor.fetchone()['count']

        # Approved listings
        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE approval_status='approved'")
        stats['approved_listings'] = cursor.fetchone()['count']

        # Sold products
        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE approval_status='sold'")
        stats['sold_listings'] = cursor.fetchone()['count']

        # Total complaints
        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status='pending'")
        stats['pending_complaints'] = cursor.fetchone()['count']

        # Recent listings (last 7 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM listings 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        stats['recent_listings'] = cursor.fetchall()

        # Recent users (last 7 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM users 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) AND role != 'admin'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        stats['recent_users'] = cursor.fetchall()

        # Recent activity
        cursor.execute("""
            SELECT u.username, al.activity_type, al.description, al.created_at
            FROM activity_logs al
            JOIN users u ON al.user_id = u.id
            ORDER BY al.created_at DESC
            LIMIT 10
        """)
        stats['recent_activity'] = cursor.fetchall()

        # Top sellers (by listing count)
        cursor.execute("""
            SELECT u.username, COUNT(l.id) as listing_count
            FROM users u
            LEFT JOIN listings l ON u.id = l.user_id
            WHERE u.role = 'seller'
            GROUP BY u.id
            ORDER BY listing_count DESC
            LIMIT 5
        """)
        stats['top_sellers'] = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("admin/admin_dashboard.html", stats=stats)

    except Exception as e:
        flash(f"❌ Error loading dashboard: {str(e)}", "error")
        return redirect(url_for("home"))

# ==============================
# USER MANAGEMENT ROUTES
# ==============================

@admin_bp.route("/users", methods=["GET"])
@admin_required
def manage_users():
    """List all users with search and filter"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        role_filter = request.args.get('role', '')
        items_per_page = 10

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Build query with filters
        query = "SELECT id, username, email, role, phone, created_at FROM users WHERE role != 'admin'"
        params = []

        if search:
            query += " AND (username LIKE %s OR email LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        if role_filter:
            query += " AND role = %s"
            params.append(role_filter)

        # Get total count
        count_query = query.replace("SELECT id, username, email, role, phone, created_at", "SELECT COUNT(*) as total")
        cursor.execute(count_query, params)
        row = cursor.fetchone()
        total = row['total'] if row else 0

        # Get paginated results
        offset = (page - 1) * items_per_page
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([items_per_page, offset])

        cursor.execute(query, params)
        users = cursor.fetchall()

        total_pages = (total + items_per_page - 1) // items_per_page

        cursor.close()
        conn.close()

        return render_template("admin/admin_users.html", 
                             users=users, 
                             total_pages=total_pages, 
                             current_page=page,
                             search=search,
                             role_filter=role_filter,
                             total=total)

    except Exception as e:
        flash(f"❌ Error loading users: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route("/user/<int:user_id>", methods=["GET"])
@admin_required
def view_user(user_id):
    """View detailed user profile"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get user details
        cursor.execute("""
            SELECT id, username, email, phone, role, created_at, warning_count, suspension_reason
            FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()

        if not user:
            flash("❌ User not found", "error")
            return redirect(url_for("admin.manage_users"))

        # Get user's listings
        cursor.execute("""
            SELECT id, title, price, approval_status, created_at
            FROM listings WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id,))
        listings = cursor.fetchall()

        # Get complaints about this user
        cursor.execute("""
            SELECT id, complaint_type, reason, status, created_at
            FROM complaints WHERE reported_user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id,))
        complaints = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("admin/admin_user_detail.html", 
                             user=user, 
                             listings=listings, 
                             complaints=complaints)

    except Exception as e:
        flash(f"❌ Error loading user: {str(e)}", "error")
        return redirect(url_for("admin.manage_users"))

@admin_bp.route("/user/<int:user_id>/block", methods=["POST"])
@admin_required
def block_user(user_id):
    """Block a user"""
    try:
        admin_id = session.get('user_id')
        reason = request.form.get('reason', 'No reason provided')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET role='blocked', suspension_reason=%s WHERE id=%s", 
                      (reason, user_id))
        conn.commit()

        log_admin_action(admin_id, 'BLOCK_USER', f"Blocked user {user_id}. Reason: {reason}", 'users', user_id)

        cursor.close()
        conn.close()

        flash("✅ User blocked successfully", "success")
    except Exception as e:
        flash(f"❌ Error blocking user: {str(e)}", "error")

    return redirect(url_for("admin.view_user", user_id=user_id))

@admin_bp.route("/user/<int:user_id>/unblock", methods=["POST"])
@admin_required
def unblock_user(user_id):
    """Unblock a user"""
    try:
        admin_id = session.get('user_id')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET role='buyer', suspension_reason=NULL WHERE id=%s", (user_id,))
        conn.commit()

        log_admin_action(admin_id, 'UNBLOCK_USER', f"Unblocked user {user_id}", 'users', user_id)

        cursor.close()
        conn.close()

        flash("✅ User unblocked successfully", "success")
    except Exception as e:
        flash(f"❌ Error unblocking user: {str(e)}", "error")

    return redirect(url_for("admin.view_user", user_id=user_id))

# ==============================
# PRODUCT MANAGEMENT ROUTES
# ==============================

@admin_bp.route("/products", methods=["GET"])
@admin_required
def manage_products():
    """List all products with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', 'all')
        search = request.args.get('search', '')
        items_per_page = 10

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        base_select = ("SELECT l.id, l.title, l.price, l.approval_status, l.category, l.user_id, "
                       "u.username, l.created_at FROM listings l JOIN users u ON l.user_id = u.id")
        where_clauses = []
        params = []

        if status_filter != 'all':
            where_clauses.append("l.approval_status = %s")
            params.append(status_filter)

        if search:
            where_clauses.append("(l.title LIKE %s OR u.username LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])

        where_sql = ''
        if where_clauses:
            where_sql = ' WHERE ' + ' AND '.join(where_clauses)

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM listings l JOIN users u ON l.user_id = u.id" + ((' WHERE ' + ' AND '.join(where_clauses)) if where_clauses else '')
        cursor.execute(count_query, params)
        row = cursor.fetchone()
        total = row['total'] if row else 0

        # Get paginated results
        offset = (page - 1) * items_per_page
        select_query = base_select + where_sql + " ORDER BY FIELD(l.approval_status, 'pending', 'rejected', 'approved', 'sold'), l.created_at DESC LIMIT %s OFFSET %s"
        exec_params = params + [items_per_page, offset]
        cursor.execute(select_query, exec_params)
        products = cursor.fetchall()

        total_pages = (total + items_per_page - 1) // items_per_page

        cursor.close()
        conn.close()

        return render_template("admin/admin_products.html", 
                             products=products,
                             total_pages=total_pages,
                             current_page=page,
                             status_filter=status_filter,
                             search=search,
                             total=total)

    except Exception as e:
        import traceback as _tb
        tb = _tb.format_exc()
        try:
            with open('admin_products_error.log', 'a', encoding='utf-8') as _f:
                _f.write(f"---\nTime: {datetime.now()}\nError: {str(e)}\nTrace:\n{tb}\n")
        except Exception:
            pass
        app.logger.exception("Error loading admin products")
        flash(f"❌ Error loading products: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route("/product/<int:product_id>/approve", methods=["POST"])
@admin_required
def approve_product(product_id):
    """Approve a product listing"""
    try:
        admin_id = session.get('user_id')
        notes = request.form.get('notes', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE listings 
            SET approval_status='approved', admin_notes=%s, approved_by=%s, approved_at=NOW()
            WHERE id=%s
        """, (notes, admin_id, product_id))
        conn.commit()

        log_admin_action(admin_id, 'APPROVE_PRODUCT', f"Approved listing {product_id}. Notes: {notes}", 
                        'listings', product_id)

        cursor.close()
        conn.close()

        flash("✅ Product approved successfully", "success")
    except Exception as e:
        flash(f"❌ Error approving product: {str(e)}", "error")

    return redirect(request.referrer or url_for("admin.manage_products"))

@admin_bp.route("/product/<int:product_id>/reject", methods=["POST"])
@admin_required
def reject_product(product_id):
    """Reject a product listing"""
    try:
        admin_id = session.get('user_id')
        reason = request.form.get('reason', 'No reason provided')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE listings 
            SET approval_status='rejected', admin_notes=%s, approved_by=%s, approved_at=NOW()
            WHERE id=%s
        """, (reason, admin_id, product_id))
        conn.commit()

        log_admin_action(admin_id, 'REJECT_PRODUCT', f"Rejected listing {product_id}. Reason: {reason}", 
                        'listings', product_id)

        cursor.close()
        conn.close()

        flash("✅ Product rejected successfully", "success")
    except Exception as e:
        flash(f"❌ Error rejecting product: {str(e)}", "error")

    return redirect(request.referrer or url_for("admin.manage_products"))

@admin_bp.route("/product/<int:product_id>/delete", methods=["POST"])
@admin_required
def delete_product(product_id):
    """Delete a product listing"""
    try:
        admin_id = session.get('user_id')
        reason = request.form.get('reason', 'No reason provided')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM listings WHERE id=%s", (product_id,))
        conn.commit()

        log_admin_action(admin_id, 'DELETE_PRODUCT', f"Deleted listing {product_id}. Reason: {reason}", 
                        'listings', product_id)

        cursor.close()
        conn.close()

        flash("✅ Product deleted successfully", "success")
    except Exception as e:
        flash(f"❌ Error deleting product: {str(e)}", "error")

    return redirect(request.referrer or url_for("admin.manage_products"))

# ==============================
# COMPLAINTS & REPORTS ROUTES
# ==============================

@admin_bp.route("/complaints", methods=["GET"])
@admin_required
def manage_complaints():
    """List all complaints"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', 'pending')
        items_per_page = 10

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT c.id, c.complaint_type, c.reason, c.status, c.created_at,
                   r.username as reporter, u.username as reported_user, l.title as listing_title
            FROM complaints c
            LEFT JOIN users r ON c.reporter_id = r.id
            LEFT JOIN users u ON c.reported_user_id = u.id
            LEFT JOIN listings l ON c.listing_id = l.id
            WHERE c.status = %s
            ORDER BY c.created_at DESC
        """
        params = [status_filter]

        # Get total count
        cursor.execute("""
            SELECT COUNT(*) as total FROM complaints WHERE status = %s
        """, [status_filter])
        row = cursor.fetchone()
        total = row['total'] if row else 0

        # Get paginated results
        offset = (page - 1) * items_per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([items_per_page, offset])

        cursor.execute(query, params)
        complaints = cursor.fetchall()

        total_pages = (total + items_per_page - 1) // items_per_page

        cursor.close()
        conn.close()

        return render_template("admin/admin_complaints.html",
                             complaints=complaints,
                             total_pages=total_pages,
                             current_page=page,
                             status_filter=status_filter,
                             total=total)

    except Exception as e:
        flash(f"❌ Error loading complaints: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route("/complaint/<int:complaint_id>/resolve", methods=["POST"])
@admin_required
def resolve_complaint(complaint_id):
    """Mark complaint as resolved"""
    try:
        admin_id = session.get('user_id')
        action = request.form.get('action', 'dismiss')
        notes = request.form.get('notes', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get complaint details
        cursor.execute("SELECT * FROM complaints WHERE id=%s", (complaint_id,))
        complaint = cursor.fetchone()

        if not complaint:
            flash("❌ Complaint not found", "error")
            return redirect(url_for("admin.manage_complaints"))

        # Update complaint status
        status = 'dismissed' if action == 'dismiss' else 'resolved'
        cursor.execute("""
            UPDATE complaints
            SET status=%s, admin_action=%s, admin_id=%s, resolved_at=NOW()
            WHERE id=%s
        """, (status, notes, admin_id, complaint_id))

        # If action is warn/block, update user
        if action == 'warn' and complaint['reported_user_id']:
            cursor.execute("""
                UPDATE users
                SET warning_count = warning_count + 1, last_warning_at=NOW()
                WHERE id=%s
            """, (complaint['reported_user_id'],))

            # Block if 3 warnings
            cursor.execute("SELECT warning_count FROM users WHERE id=%s", (complaint['reported_user_id'],))
            user = cursor.fetchone()
            if user['warning_count'] >= 3:
                cursor.execute("""
                    UPDATE users SET role='blocked', suspension_reason='Automatic suspension after 3 warnings'
                    WHERE id=%s
                """, (complaint['reported_user_id'],))

        elif action == 'block' and complaint['reported_user_id']:
            cursor.execute("""
                UPDATE users SET role='blocked', suspension_reason=%s
                WHERE id=%s
            """, (notes, complaint['reported_user_id']))

        conn.commit()
        log_admin_action(admin_id, f'COMPLAINT_{action.upper()}', 
                        f"Processed complaint {complaint_id}. Action: {action}", 'complaints', complaint_id)

        cursor.close()
        conn.close()

        flash(f"✅ Complaint {status} successfully", "success")
    except Exception as e:
        flash(f"❌ Error resolving complaint: {str(e)}", "error")

    return redirect(request.referrer or url_for("admin.manage_complaints"))

# ==============================
# ANALYTICS/ACTIVITY ROUTES
# ==============================

@admin_bp.route("/activity", methods=["GET"])
@admin_required
def activity_logs():
    """View admin activity logs"""
    try:
        page = request.args.get('page', 1, type=int)
        items_per_page = 20

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT al.id, al.action, al.description, al.created_at, u.username
            FROM admin_logs al
            JOIN users u ON al.admin_id = u.id
            ORDER BY al.created_at DESC
        """

        cursor.execute("SELECT COUNT(*) as total FROM admin_logs")
        row = cursor.fetchone()
        total = row['total'] if row else 0

        offset = (page - 1) * items_per_page
        query += " LIMIT %s OFFSET %s"

        cursor.execute(query, [items_per_page, offset])
        logs = cursor.fetchall()

        total_pages = (total + items_per_page - 1) // items_per_page

        cursor.close()
        conn.close()

        return render_template("admin/admin_activity.html",
                             logs=logs,
                             total_pages=total_pages,
                             current_page=page,
                             total=total)

    except Exception as e:
        flash(f"❌ Error loading activity logs: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route("/api/chart-data")
@admin_required
def chart_data():
    """API endpoint for chart data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Product growth (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM listings
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        product_data = cursor.fetchall()

        # User growth (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) AND role != 'admin'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        user_data = cursor.fetchall()

        # Category distribution
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM listings
            WHERE approval_status = 'approved'
            GROUP BY category
            LIMIT 10
        """)
        category_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'products': product_data,
            'users': user_data,
            'categories': category_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
