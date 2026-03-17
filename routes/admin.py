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

@admin_bp.context_processor
def inject_admin_defaults():
    return {
        'stats': {
            'pending_complaints': 0
        }
    }

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
# BOOSTED LISTINGS
# ==============================
@admin_bp.route("/boosted")
@admin_required
def boosted_listings():
    """Manage boosted/promotion listings from boosted_listings table"""
    records = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        # Fetch from boosted_listings table as requested
        cur.execute("""
            SELECT bl.id, bl.listing_id, bl.seller_id, bl.boost_type, 
                   bl.start_date, bl.end_date, bl.status,
                   COALESCE(l.title, 'Deleted Listing') as title, 
                   COALESCE(u.username, 'Unknown Seller') as username
            FROM boosted_listings bl
            LEFT JOIN listings l ON bl.listing_id = l.id
            LEFT JOIN users u ON bl.seller_id = u.id
            ORDER BY bl.start_date DESC
        """)
        records = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        app.logger.error(f"Error fetching boosted listings: {e}")
        records = []
    return render_template("admin/admin_boosted.html", records=records)

@admin_bp.route("/boosted/disable/<int:boost_id>", methods=["POST"])
@admin_required
def disable_boost(boost_id):
    """Disable a boosted listing"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE boosted_listings SET status='disabled' WHERE id=%s", (boost_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("✅ Boost disabled successfully", "success")
    except Exception as e:
        flash(f"❌ Error disabling boost: {e}", "error")
    return redirect(url_for("admin.boosted_listings"))

@admin_bp.route("/boosted/extend/<int:boost_id>", methods=["POST"])
@admin_required
def extend_boost(boost_id):
    """Extend a boosted listing by 7 days"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE boosted_listings SET end_date = DATE_ADD(end_date, INTERVAL 7 DAY), status='active' WHERE id=%s", (boost_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("✅ Boost extended by 7 days", "success")
    except Exception as e:
        flash(f"❌ Error extending boost: {e}", "error")
    return redirect(url_for("admin.boosted_listings"))

@admin_bp.route("/boosted-ads")
@admin_required
def boosted_ads_alias():
    return boosted_listings()

@admin_bp.route("/boost-sales")
@admin_required
def boost_sales():
    rows = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT pay.id, u.username, l.title, l.status as listing_status,
                       bp.name as package_name, pay.amount, pay.method, pay.status, pay.created_at,
                       b.status as promotion_status
                FROM payments pay
                JOIN users u ON u.id=pay.user_id
                LEFT JOIN listings l ON l.id=pay.ad_id
                LEFT JOIN boost_packages bp ON bp.id=pay.package_id
                LEFT JOIN ad_boosts b ON b.payment_id = pay.id
                WHERE pay.ad_id IS NOT NULL
                ORDER BY pay.created_at DESC
                LIMIT 200
            """)
            rows = cur.fetchall()
        except Exception:
            rows = []
        cur.close()
        conn.close()
    except Exception:
        rows = []
    return render_template("admin/admin_payments.html", payments=rows, stats={})

# ==============================
# CATEGORIES MANAGEMENT (index)
# ==============================
@admin_bp.route("/categories")
@admin_required
def manage_categories():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, name, icon FROM categories ORDER BY name")
        categories = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("admin/admin_categories.html", categories=categories)
    except Exception as e:
        flash(f"❌ Error loading categories: {e}", "error")
        return redirect(url_for("admin.dashboard"))

# ==============================
# TRANSACTIONS & REVENUE
# ==============================
@admin_bp.route("/revenue")
@admin_required
def revenue():
    payments = []
    stats = {
        "total_revenue": 0,
        "monthly_revenue": 0,
        "total_transactions": 0,
        "avg_transaction": 0
    }
    monthly_revenue_labels = []
    monthly_revenue_data = []
    payment_method_labels = []
    payment_method_counts = []
    available_months = []
    selected_month = request.args.get('month', '')
    payment_method = request.args.get('method', '')

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Stats
        try:
            cur.execute("SELECT COALESCE(SUM(amount),0) as total FROM payments WHERE status='paid'")
            stats["total_revenue"] = cur.fetchone()["total"]
        except Exception:
            stats["total_revenue"] = 0

        try:
            cur.execute("SELECT COALESCE(SUM(amount),0) as total FROM payments WHERE status='paid' AND YEAR(created_at)=YEAR(NOW()) AND MONTH(created_at)=MONTH(NOW())")
            stats["monthly_revenue"] = cur.fetchone()["total"]
        except Exception:
            stats["monthly_revenue"] = 0

        try:
            cur.execute("SELECT COUNT(*) as cnt, COALESCE(AVG(amount),0) as avg_amt FROM payments WHERE status='paid'")
            row = cur.fetchone()
            stats["total_transactions"] = row["cnt"]
            stats["avg_transaction"] = row["avg_amt"]
        except Exception:
            pass

        # Monthly revenue trend (last 6 months)
        try:
            cur.execute("""
                SELECT DATE_FORMAT(created_at, '%b %Y') as ym, SUM(amount) as amt
                FROM payments 
                WHERE status='paid' 
                AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY DATE_FORMAT(created_at, '%Y-%m')
                ORDER BY MIN(created_at)
            """)
            rows = cur.fetchall()
            monthly_revenue_labels = [r["ym"] for r in rows]
            monthly_revenue_data = [float(r["amt"]) for r in rows]
        except Exception:
            monthly_revenue_labels = []
            monthly_revenue_data = []

        # Payment method distribution
        try:
            cur.execute("""
                SELECT method as payment_method, COUNT(*) as cnt 
                FROM payments 
                WHERE status='paid'
                GROUP BY method
            """)
            rows = cur.fetchall()
            payment_method_labels = [ (r["payment_method"] or "unknown").title().replace('_',' ') for r in rows ]
            payment_method_counts = [ r["cnt"] for r in rows ]
        except Exception:
            payment_method_labels = []
            payment_method_counts = []

        # Available months dropdown
        try:
            cur.execute("""
                SELECT DISTINCT DATE_FORMAT(created_at, '%b %Y') as ym
                FROM payments
                ORDER BY MIN(created_at) DESC
            """)
            available_months = [r["ym"] for r in cur.fetchall()]
        except Exception:
            available_months = []

        # Payments table (join users and compute gst/total)
        where = []
        params = []
        if selected_month:
            where.append("DATE_FORMAT(p.created_at, '%b %Y') = %s")
            params.append(selected_month)
        if payment_method:
            where.append("p.method = %s")
            params.append(payment_method)
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        try:
            cur.execute(f"""
                SELECT p.id, p.user_id, p.amount, p.method as payment_method, p.status, p.created_at as paid_at,
                       u.username, u.email
                FROM payments p
                JOIN users u ON p.user_id = u.id
                {where_sql}
                ORDER BY p.created_at DESC
                LIMIT 200
            """, tuple(params))
            rows = cur.fetchall()
            payments = []
            for r in rows:
                amt = float(r["amount"] or 0)
                gst = round(amt * 0.18, 2)
                total = round(amt + gst, 2)
                payments.append({
                    "id": r["id"],
                    "username": r.get("username", "User"),
                    "email": r.get("email", ""),
                    "plan": None,
                    "amount": amt,
                    "gst": gst,
                    "total_amount": total,
                    "payment_method": r.get("payment_method", "unknown"),
                    "paid_at": r.get("paid_at")
                })
        except Exception:
            payments = []

        cur.close()
        conn.close()
    except Exception:
        pass

    return render_template(
        "admin/admin_payments.html",
        payments=payments,
        stats=stats,
        monthly_revenue_labels=monthly_revenue_labels,
        monthly_revenue_data=monthly_revenue_data,
        payment_method_labels=payment_method_labels,
        payment_method_counts=payment_method_counts,
        available_months=available_months,
        selected_month=selected_month,
        payment_method=payment_method
    )

# ==============================
# ANALYTICS & INSIGHTS
# ==============================
@admin_bp.route("/analytics")
@admin_required
def analytics():
    insights = {}
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        # KPIs
        try:
            cur.execute("SELECT COUNT(*) as c FROM users WHERE role!='admin'")
            total_users = cur.fetchone()["c"]
        except Exception:
            total_users = 0
        try:
            cur.execute("SELECT COUNT(*) as c FROM listings")
            total_listings = cur.fetchone()["c"]
        except Exception:
            total_listings = 0
        try:
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='active' AND approval_status='approved'")
            active_listings = cur.fetchone()["c"]
        except Exception:
            active_listings = 0
        # boosted ads
        try:
            cur.execute("SELECT COUNT(*) as c FROM ad_boosts WHERE status='active' AND expiry_date>NOW()")
            boosted_ads = cur.fetchone()["c"]
        except Exception:
            boosted_ads = 0
        # revenue
        try:
            cur.execute("SELECT COALESCE(SUM(amount),0) as s FROM payments WHERE status IN ('success','paid')")
            total_revenue = float(cur.fetchone()["s"] or 0)
        except Exception:
            total_revenue = 0.0
        # new users this week
        try:
            cur.execute("SELECT COUNT(*) as c FROM users WHERE created_at>=DATE_SUB(NOW(), INTERVAL 7 DAY)")
            new_users_week = cur.fetchone()["c"]
        except Exception:
            new_users_week = 0
        # delta vs previous week
        try:
            cur.execute("""
                SELECT 
                  SUM(CASE WHEN created_at>=DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as this_wk,
                  SUM(CASE WHEN created_at<DATE_SUB(NOW(), INTERVAL 7 DAY) AND created_at>=DATE_SUB(NOW(), INTERVAL 14 DAY) THEN 1 ELSE 0 END) as prev_wk
                FROM users
            """)
            r = cur.fetchone()
            new_users_week_prev = int(r["prev_wk"] or 0)
            new_users_week_delta = new_users_week - new_users_week_prev
        except Exception:
            new_users_week_delta = 0
        # revenue by month (last 6-8 months)
        rev_labels, rev_values = [], []
        try:
            cur.execute("""
                SELECT DATE_FORMAT(created_at,'%b %Y') as ym, SUM(amount) as amt, MIN(created_at) as d
                FROM payments WHERE status IN ('success','paid')
                GROUP BY DATE_FORMAT(created_at,'%Y-%m')
                ORDER BY MIN(created_at) ASC
                LIMIT 12
            """)
            rows = cur.fetchall()
            rev_labels = [r["ym"] for r in rows]
            rev_values = [float(r["amt"] or 0) for r in rows]
        except Exception:
            pass
        # revenue growth percent MoM
        revenue_growth_pct = 0
        if len(rev_values) >= 2:
            prev = rev_values[-2] or 0
            curr = rev_values[-1] or 0
            revenue_growth_pct = int(((curr - prev) / prev) * 100) if prev else (100 if curr > 0 else 0)
        # listings per day (last 14 days)
        lst_day_labels, lst_day_counts = [], []
        try:
            cur.execute("""
                SELECT DATE(created_at) as d, COUNT(*) as c
                FROM listings
                WHERE created_at>=DATE_SUB(NOW(), INTERVAL 14 DAY)
                GROUP BY DATE(created_at) ORDER BY d
            """)
            rows = cur.fetchall()
            lst_day_labels = [r["d"].strftime("%d %b") for r in rows]
            lst_day_counts = [int(r["c"] or 0) for r in rows]
        except Exception:
            pass
        # active vs sold
        active_vs_sold = [0, 0]
        try:
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='active'")
            active_vs_sold[0] = cur.fetchone()["c"]
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='sold' OR approval_status='sold'")
            active_vs_sold[1] = cur.fetchone()["c"]
        except Exception:
            pass
        # listings by category & top 10
        cat_labels, cat_counts = [], []
        try:
            cur.execute("""
                SELECT category, COUNT(*) as c FROM listings
                GROUP BY category ORDER BY c DESC LIMIT 10
            """)
            rows = cur.fetchall()
            cat_labels = [r["category"] for r in rows if r["category"]]
            cat_counts = [int(r["c"]) for r in rows if r["category"]]
        except Exception:
            pass
        top_category = cat_labels[0] if cat_labels else ""
        top_category_count = cat_counts[0] if cat_counts else 0
        # user growth daily (last 14 days)
        usr_day_labels, usr_day_counts = [], []
        try:
            cur.execute("""
                SELECT DATE(created_at) as d, COUNT(*) as c
                FROM users
                WHERE created_at>=DATE_SUB(NOW(), INTERVAL 14 DAY)
                GROUP BY DATE(created_at) ORDER BY d
            """)
            rows = cur.fetchall()
            usr_day_labels = [r["d"].strftime("%d %b") for r in rows]
            usr_day_counts = [int(r["c"] or 0) for r in rows]
        except Exception:
            pass
        # new users this month/year
        try:
            cur.execute("SELECT COUNT(*) as c FROM users WHERE YEAR(created_at)=YEAR(NOW()) AND MONTH(created_at)=MONTH(NOW())")
            new_users_this_month = cur.fetchone()["c"]
        except Exception:
            new_users_this_month = 0
        try:
            cur.execute("SELECT COUNT(*) as c FROM users WHERE YEAR(created_at)=YEAR(NOW())")
            new_users_this_year = cur.fetchone()["c"]
        except Exception:
            new_users_this_year = 0
        # health metrics
        listing_completion_rate = 0
        user_engagement_rate = 0
        boost_usage_pct = 0
        active_users_7d = 0
        try:
            cur.execute("SELECT COUNT(*) as c FROM listings")
            total_l = cur.fetchone()["c"] or 0
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE COALESCE(description,'')<>'' AND COALESCE(photos,'')<>''")
            complete_l = cur.fetchone()["c"] or 0
            listing_completion_rate = int((complete_l/total_l)*100) if total_l else 0
        except Exception:
            pass
        try:
            # engagement: messages in last 7 days per active listing ratio scaled to %
            cur.execute("SELECT COUNT(*) as c FROM messages WHERE created_at>=DATE_SUB(NOW(), INTERVAL 7 DAY)")
            msg7 = cur.fetchone()["c"] or 0
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='active'")
            act = cur.fetchone()["c"] or 0
            user_engagement_rate = min(100, int((msg7 / max(act,1)) * 20))  # heuristic scale
        except Exception:
            pass
        try:
            boost_usage_pct = int((boosted_ads / max(active_listings,1)) * 100) if active_listings else 0
        except Exception:
            pass
        try:
            cur.execute("""
                SELECT COUNT(DISTINCT user_id) as c FROM (
                    SELECT user_id, created_at FROM listings WHERE created_at>=DATE_SUB(NOW(), INTERVAL 7 DAY)
                    UNION ALL
                    SELECT sender_id as user_id, created_at FROM messages WHERE created_at>=DATE_SUB(NOW(), INTERVAL 7 DAY)
                ) t
            """)
            active_users_7d = cur.fetchone()["c"] or 0
        except Exception:
            pass
        # boosted ads performance
        boosts_total, boosts_revenue, boosted_cat_labels, boosted_cat_counts = 0, 0, [], []
        try:
            cur.execute("SELECT COUNT(*) as c FROM ad_boosts")
            boosts_total = cur.fetchone()["c"] or 0
        except Exception:
            pass
        try:
            cur.execute("SELECT COALESCE(SUM(amount),0) as s FROM payments WHERE package_id IS NOT NULL AND status IN ('success','paid')")
            boosts_revenue = float(cur.fetchone()["s"] or 0)
        except Exception:
            pass
        try:
            cur.execute("""
                SELECT l.category, COUNT(*) as c
                FROM ad_boosts b
                JOIN listings l ON b.ad_id=l.id
                GROUP BY l.category
                ORDER BY c DESC
                LIMIT 5
            """)
            rows = cur.fetchall()
            boosted_cat_labels = [r["category"] for r in rows if r["category"]]
            boosted_cat_counts = [int(r["c"]) for r in rows if r["category"]]
        except Exception:
            pass
        # automatic insights
        auto_insights = []
        try:
            auto_insights.append(f"Revenue {'increased' if revenue_growth_pct>=0 else 'decreased'} {abs(revenue_growth_pct)}% compared to last month")
            if top_category:
                auto_insights.append(f"'{top_category}' has the highest listings")
            if new_users_week_delta >= 0:
                auto_insights.append("User registrations increased this week")
            else:
                auto_insights.append("User registrations decreased this week")
        except Exception:
            pass
        # recent activity
        recent = []
        try:
            cur.execute("SELECT 'user' as t, username as title, created_at FROM users ORDER BY created_at DESC LIMIT 5")
            recent += [{"type":"user","title":r["title"],"created_at":r["created_at"].strftime("%d %b %H:%M")} for r in cur.fetchall()]
        except Exception:
            pass
        try:
            cur.execute("SELECT 'listing' as t, title, created_at FROM listings ORDER BY created_at DESC LIMIT 5")
            recent += [{"type":"listing","title":r["title"],"created_at":r["created_at"].strftime("%d %b %H:%M")} for r in cur.fetchall()]
        except Exception:
            pass
        try:
            cur.execute("""
                SELECT 'boost' as t, CONCAT('Boost purchased for Ad #', ad_id) as title, created_at 
                FROM payments WHERE package_id IS NOT NULL ORDER BY created_at DESC LIMIT 5
            """)
            recent += [{"type":"boost","title":r["title"],"created_at":r["created_at"].strftime("%d %b %H:%M")} for r in cur.fetchall()]
        except Exception:
            pass
        # finalize insights
        insights = {
            "kpis": {
                "total_users": total_users,
                "total_listings": total_listings,
                "active_listings": active_listings,
                "boosted_ads": boosted_ads,
                "total_revenue": int(total_revenue),
                "new_users_week": new_users_week,
                "new_users_week_delta": new_users_week_delta
            },
            "revenue_month_labels": rev_labels,
            "revenue_month_totals": rev_values,
            "revenue_growth_pct": revenue_growth_pct,
            "listings_day_labels": lst_day_labels,
            "listings_day_counts": lst_day_counts,
            "active_vs_sold": active_vs_sold,
            "category_labels": cat_labels,
            "category_counts": cat_counts,
            "top_category": top_category,
            "top_category_count": top_category_count,
            "user_day_labels": usr_day_labels,
            "user_day_counts": usr_day_counts,
            "new_users_this_month": new_users_this_month,
            "new_users_this_year": new_users_this_year,
            "avg_users_per_day": int(sum(usr_day_counts)/max(len(usr_day_counts),1)),
            "listing_completion_rate": listing_completion_rate,
            "user_engagement_rate": user_engagement_rate,
            "boost_usage_pct": boost_usage_pct,
            "active_users_7d": active_users_7d,
            "boosts_total": boosts_total,
            "boosts_revenue": int(boosts_revenue),
            "boosted_cat_labels": boosted_cat_labels,
            "boosted_cat_counts": boosted_cat_counts,
            "auto_insights": auto_insights,
            "recent": recent,
            "seller_activity_rate": 0,
            "subscription_mix": { "basic": 0, "standard": 0, "premium": 0 },
            "peak_revenue_day": "",
            "most_sold_category": "",
            "avg_listing_price": 0,
            "churn_rate": 0
        }
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template("admin/admin_insights.html", insights=insights)

# ==============================
# SETTINGS
# ==============================
@admin_bp.route("/settings")
@admin_required
def settings():
    return render_template("admin/admin_settings.html")

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

        # Build query with filters (only columns guaranteed to exist)
        query = "SELECT id, username, email, role, phone, created_at FROM users WHERE role != 'admin'"
        params = []

        if search:
            query += " AND (username LIKE %s OR email LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        if role_filter:
            query += " AND role = %s"
            params.append(role_filter)

        # Get total count: build a COUNT(*) query using the same filters to avoid
        # mixing aggregated and non-aggregated columns (prevents ONLY_FULL_GROUP_BY errors)
        try:
            count_query = "SELECT COUNT(*) as total FROM users WHERE role != 'admin'"
            count_params = []
            if search:
                count_query += " AND (username LIKE %s OR email LIKE %s)"
                count_params.extend([f"%{search}%", f"%{search}%"])
            if role_filter:
                count_query += " AND role = %s"
                count_params.append(role_filter)

            cursor.execute(count_query, count_params)
            row = cursor.fetchone()
            total = row['total'] if row else 0
        except Exception:
            total = 0

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

        # Get user details (skip optional columns that may not exist in this schema)
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

        # Using LEFT JOIN so that listings show up even if the user record is missing
        base_select = ("SELECT l.id, l.title, l.price, l.approval_status, l.category, l.user_id, "
                       "COALESCE(u.username, 'Deleted User') as username, l.created_at "
                       "FROM listings l LEFT JOIN users u ON l.user_id = u.id")
        where_clauses = []
        params = []

        if status_filter != 'all':
            where_clauses.append("l.approval_status = %s")
            params.append(status_filter)

        if search:
            where_clauses.append("(l.title LIKE %s OR u.username LIKE %s OR l.id LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        where_sql = ''
        if where_clauses:
            where_sql = ' WHERE ' + ' AND '.join(where_clauses)

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM listings l LEFT JOIN users u ON l.user_id = u.id" + ((' WHERE ' + ' AND '.join(where_clauses)) if where_clauses else '')
        cursor.execute(count_query, params)
        row = cursor.fetchone()
        total = row['total'] if row else 0

        # Get paginated results
        offset = (page - 1) * items_per_page
        select_query = base_select + where_sql + " ORDER BY FIELD(l.approval_status, 'pending', 'rejected', 'approved', 'sold'), l.id DESC LIMIT %s OFFSET %s"
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
