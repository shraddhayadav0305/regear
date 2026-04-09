"""
Admin Routes - Complete Admin Dashboard Backend
Handles all admin functionality: users, products, complaints, analytics
"""

from flask import Blueprint, render_template, request, redirect, session, flash, url_for, jsonify, current_app
import mysql.connector
from datetime import datetime, timedelta
import json

from transactions_helpers import (
    map_payment_method,
    map_transaction_status,
    calculate_gst,
    calculate_total
)

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


def table_exists(cursor, table_name):
    cursor.execute(
        """
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_name = %s
        """,
        (table_name,)
    )
    return cursor.fetchone()["count"] > 0


def column_exists(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT COUNT(*) as count
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s
        """,
        (table_name, column_name)
    )
    return cursor.fetchone()["count"] > 0


def get_payment_total_expression(cursor):
    if column_exists(cursor, "payments", "total_amount"):
        return "COALESCE(total_amount,0)"
    if column_exists(cursor, "payments", "amount"):
        if column_exists(cursor, "payments", "gst"):
            return "COALESCE(amount,0) + COALESCE(gst,0)"
        return "COALESCE(amount,0)"
    return "0"


def get_payment_status_filter():
    return "status IN ('completed', 'paid', 'success')"


def safe_percent(new_value, old_value):
    if old_value and old_value != 0:
        return int(((new_value - old_value) / old_value) * 100)
    return 100 if new_value > 0 else 0


def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            wants_json = request.args.get('json') == '1' or 'application/json' in request.headers.get('Accept', '')
            if wants_json:
                return jsonify({"error": "Admin access required"}), 401
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

def fetch_admin_dashboard_stats(cursor):
    stats = {
        "total_users": 0,
        "active_users": 0,
        "new_users_7_days": 0,
        "new_users_today": 0,
        "new_users_growth": 0,
        "total_listings": 0,
        "active_listings": 0,
        "new_listings_7_days": 0,
        "listings_today": 0,
        "listings_growth": 0,
        "boosted_ads_active": 0,
        "total_transactions": 0,
        "total_revenue": 0.0,
        "revenue_month": 0.0,
        "active_sellers": 0,
        "blocked_users": 0,
        "pending_complaints": 0,
        "category_distribution": [],
        "listings_growth_trend": [],
        "revenue_trend": []
    }

    # User counts
    cursor.execute("SELECT COUNT(*) as c FROM users")
    stats["total_users"] = int(cursor.fetchone()["c"] or 0)

    cursor.execute("SELECT COUNT(*) as c FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
    stats["new_users_7_days"] = int(cursor.fetchone()["c"] or 0)

    if column_exists(cursor, "users", "created_at"):
        cursor.execute("SELECT COUNT(*) as c FROM users WHERE DATE(created_at)=CURDATE()")
        stats["new_users_today"] = int(cursor.fetchone()["c"] or 0)
        cursor.execute("SELECT COUNT(*) as c FROM users WHERE DATE(created_at)=DATE_SUB(CURDATE(), INTERVAL 1 DAY)")
        yesterday_users = int(cursor.fetchone()["c"] or 0)
        stats["new_users_growth"] = int(((stats["new_users_today"] - yesterday_users) / yesterday_users) * 100) if yesterday_users else (100 if stats["new_users_today"] > 0 else 0)

    if column_exists(cursor, "users", "status"):
        cursor.execute("SELECT COUNT(*) as c FROM users WHERE status='blocked'")
        stats["blocked_users"] = int(cursor.fetchone()["c"] or 0)
    elif column_exists(cursor, "users", "role"):
        cursor.execute("SELECT COUNT(*) as c FROM users WHERE role='blocked'")
        stats["blocked_users"] = int(cursor.fetchone()["c"] or 0)

    if table_exists(cursor, "activity_logs") and column_exists(cursor, "activity_logs", "created_at"):
        cursor.execute("SELECT COUNT(DISTINCT user_id) as c FROM activity_logs WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        stats["active_users"] = int(cursor.fetchone()["c"] or 0)
    else:
        active_sources = []
        if table_exists(cursor, "listings"):
            active_sources.append("SELECT user_id FROM listings WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        if table_exists(cursor, "payments"):
            status_filter = get_payment_status_filter()
            active_sources.append(f"SELECT user_id FROM payments WHERE {status_filter} AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        if table_exists(cursor, "messages") and column_exists(cursor, "messages", "sender_id"):
            active_sources.append("SELECT sender_id as user_id FROM messages WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        if table_exists(cursor, "messages") and column_exists(cursor, "messages", "receiver_id"):
            active_sources.append("SELECT receiver_id as user_id FROM messages WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        if active_sources:
            cursor.execute("SELECT COUNT(DISTINCT user_id) as c FROM (" + " UNION ALL ".join(active_sources) + ") t")
            stats["active_users"] = int(cursor.fetchone()["c"] or 0)

    if table_exists(cursor, "listings"):
        cursor.execute("SELECT COUNT(*) as c FROM listings")
        stats["total_listings"] = int(cursor.fetchone()["c"] or 0)

        active_conditions = []
        if column_exists(cursor, "listings", "approval_status"):
            active_conditions.append("approval_status='approved'")
        if column_exists(cursor, "listings", "status"):
            active_conditions.append("status='active'")
        if column_exists(cursor, "listings", "expires_date"):
            active_conditions.append("(expires_date IS NULL OR expires_date >= NOW())")
        if column_exists(cursor, "listings", "is_sold"):
            active_conditions.append("COALESCE(is_sold,0)=0")

        active_where = " AND ".join(active_conditions) if active_conditions else "1=1"
        cursor.execute(f"SELECT COUNT(*) as c FROM listings WHERE {active_where}")
        stats["active_listings"] = int(cursor.fetchone()["c"] or 0)

        if column_exists(cursor, "listings", "created_at"):
            cursor.execute("SELECT COUNT(*) as c FROM listings WHERE DATE(created_at)=CURDATE()")
            stats["listings_today"] = int(cursor.fetchone()["c"] or 0)
            cursor.execute("SELECT COUNT(*) as c FROM listings WHERE DATE(created_at)=DATE_SUB(CURDATE(), INTERVAL 1 DAY)")
            yesterday_listings = int(cursor.fetchone()["c"] or 0)
            stats["listings_growth"] = int(((stats["listings_today"] - yesterday_listings) / yesterday_listings) * 100) if yesterday_listings else (100 if stats["listings_today"] > 0 else 0)
            cursor.execute("SELECT COUNT(*) as c FROM listings WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            stats["new_listings_7_days"] = int(cursor.fetchone()["c"] or 0)

        if column_exists(cursor, "listings", "category"):
            cursor.execute(f"""
                SELECT category, COUNT(*) as c
                FROM listings
                WHERE category IS NOT NULL AND category <> ''
                AND {active_where}
                GROUP BY category
                ORDER BY c DESC
                LIMIT 10
            """)
            stats["category_distribution"] = [
                {"category": row["category"], "count": int(row["c"] or 0)}
                for row in cursor.fetchall()
            ]

        if column_exists(cursor, "listings", "created_at"):
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM listings
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)
            rows = cursor.fetchall()
            counts_by_day = {}
            for row in rows:
                row_date = row["date"]
                if isinstance(row_date, datetime):
                    row_date = row_date.date()
                counts_by_day[row_date] = int(row["count"] or 0)

            start_date = datetime.now().date() - timedelta(days=29)
            stats["listings_growth_trend"] = [
                {"date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                 "count": counts_by_day.get(start_date + timedelta(days=i), 0)}
                for i in range(30)
            ]

            # Daily user growth series for the last 30 days
            if column_exists(cursor, "users", "created_at"):
                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM users
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY DATE(created_at)
                """)
                user_rows = cursor.fetchall()
                user_counts_by_day = {}
                for row in user_rows:
                    row_date = row["date"]
                    if isinstance(row_date, datetime):
                        row_date = row_date.date()
                    user_counts_by_day[row_date] = int(row["count"] or 0)

                stats["users_trend"] = [
                    {"date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                     "count": user_counts_by_day.get(start_date + timedelta(days=i), 0)}
                    for i in range(30)
                ]
            else:
                stats["users_trend"] = []

    if table_exists(cursor, "boosted_listings"):
        cursor.execute("SELECT COUNT(*) as c FROM boosted_listings WHERE status='active' AND end_date >= NOW()")
        stats["boosted_ads_active"] = int(cursor.fetchone()["c"] or 0)
    elif table_exists(cursor, "ad_boosts"):
        cursor.execute("SELECT COUNT(*) as c FROM ad_boosts WHERE status='active' AND expiry_date >= NOW()")
        stats["boosted_ads_active"] = int(cursor.fetchone()["c"] or 0)

    if table_exists(cursor, "transactions"):
        cursor.execute("SELECT COUNT(*) as c FROM transactions WHERE status='completed'")
        stats["total_transactions"] = int(cursor.fetchone()["c"] or 0)
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) as c FROM transactions WHERE status='completed'")
        stats["total_revenue"] = float(cursor.fetchone()["c"] or 0)
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) as c FROM transactions WHERE status='completed' AND YEAR(created_at)=YEAR(NOW()) AND MONTH(created_at)=MONTH(NOW())")
        stats["revenue_month"] = float(cursor.fetchone()["c"] or 0)
        if column_exists(cursor, "transactions", "created_at"):
            cursor.execute("""
                SELECT DATE(created_at) as date, COALESCE(SUM(total_amount),0) as total
                FROM transactions
                WHERE status='completed'
                  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)
            rows = cursor.fetchall()
            counts_by_day = {}
            for row in rows:
                row_date = row["date"]
                if isinstance(row_date, datetime):
                    row_date = row_date.date()
                counts_by_day[row_date] = float(row["total"] or 0)
            start_date = datetime.now().date() - timedelta(days=29)
            stats["revenue_trend"] = [
                {"date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                 "total": float(counts_by_day.get(start_date + timedelta(days=i), 0))}
                for i in range(30)
            ]
    elif table_exists(cursor, "payments"):
        total_expr = get_payment_total_expression(cursor)
        status_filter = get_payment_status_filter()
        cursor.execute(f"SELECT COUNT(*) as c FROM payments WHERE {status_filter}")
        stats["total_transactions"] = int(cursor.fetchone()["c"] or 0)
        cursor.execute(f"SELECT COALESCE(SUM({total_expr}),0) as c FROM payments WHERE {status_filter}")
        stats["total_revenue"] = float(cursor.fetchone()["c"] or 0)
        cursor.execute(f"SELECT COALESCE(SUM({total_expr}),0) as c FROM payments WHERE {status_filter} AND YEAR(created_at)=YEAR(NOW()) AND MONTH(created_at)=MONTH(NOW())")
        stats["revenue_month"] = float(cursor.fetchone()["c"] or 0)
        if column_exists(cursor, "payments", "created_at"):
            cursor.execute(f"""
                SELECT DATE(created_at) as date, COALESCE(SUM({total_expr}),0) as total
                FROM payments
                WHERE {status_filter}
                  AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)
            rows = cursor.fetchall()
            counts_by_day = {}
            for row in rows:
                row_date = row["date"]
                if isinstance(row_date, datetime):
                    row_date = row_date.date()
                counts_by_day[row_date] = float(row["total"] or 0)
            start_date = datetime.now().date() - timedelta(days=29)
            stats["revenue_trend"] = [
                {"date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                 "total": float(counts_by_day.get(start_date + timedelta(days=i), 0))}
                for i in range(30)
            ]

    if table_exists(cursor, "subscriptions"):
        cursor.execute("SELECT COUNT(DISTINCT user_id) as c FROM subscriptions WHERE status='active'")
        stats["active_sellers"] = int(cursor.fetchone()["c"] or 0)
    elif table_exists(cursor, "user_subscriptions"):
        cursor.execute("SELECT COUNT(DISTINCT user_id) as c FROM user_subscriptions WHERE status='active' AND end_date > NOW()")
        stats["active_sellers"] = int(cursor.fetchone()["c"] or 0)
    elif column_exists(cursor, "users", "seller_active"):
        extra_clause = "AND (subscription_end IS NULL OR subscription_end > NOW())" if column_exists(cursor, "users", "subscription_end") else ""
        cursor.execute(f"SELECT COUNT(*) as c FROM users WHERE seller_active=1 {extra_clause}")
        stats["active_sellers"] = int(cursor.fetchone()["c"] or 0)

    if table_exists(cursor, "complaints") and column_exists(cursor, "complaints", "status"):
        cursor.execute("SELECT COUNT(*) as c FROM complaints WHERE status='pending'")
        stats["pending_complaints"] = int(cursor.fetchone()["c"] or 0)

    # Revenue growth vs previous month
    if table_exists(cursor, "transactions") and column_exists(cursor, "transactions", "created_at"):
        try:
            cursor.execute("SELECT COALESCE(SUM(total_amount),0) as c FROM transactions WHERE status='completed' AND YEAR(created_at)=YEAR(DATE_SUB(NOW(), INTERVAL 1 MONTH)) AND MONTH(created_at)=MONTH(DATE_SUB(NOW(), INTERVAL 1 MONTH))")
            previous_month = float(cursor.fetchone()["c"] or 0)
            stats["revenue_growth"] = safe_percent(stats["revenue_month"], previous_month)
        except Exception:
            stats["revenue_growth"] = 0
    elif table_exists(cursor, "payments") and column_exists(cursor, "payments", "created_at"):
        try:
            total_expr = get_payment_total_expression(cursor)
            status_filter = get_payment_status_filter()
            cursor.execute(f"SELECT COALESCE(SUM({total_expr}),0) as c FROM payments WHERE {status_filter} AND YEAR(created_at)=YEAR(DATE_SUB(NOW(), INTERVAL 1 MONTH)) AND MONTH(created_at)=MONTH(DATE_SUB(NOW(), INTERVAL 1 MONTH))")
            previous_month = float(cursor.fetchone()["c"] or 0)
            stats["revenue_growth"] = safe_percent(stats["revenue_month"], previous_month)
        except Exception:
            stats["revenue_growth"] = 0

    # User growth for last 7 days vs previous 7 days
    try:
        cursor.execute("SELECT COUNT(*) as c FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        recent_week = int(cursor.fetchone()["c"] or 0)
        cursor.execute("SELECT COUNT(*) as c FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY) AND created_at < DATE_SUB(NOW(), INTERVAL 7 DAY)")
        previous_week = int(cursor.fetchone()["c"] or 0)
        stats["user_growth"] = safe_percent(recent_week, previous_week)
    except Exception:
        stats["user_growth"] = 0

    # Top categories summary
    stats["top_categories"] = stats.get("category_distribution", [])[:6]

    # Subscription stats
    stats["subscription_stats"] = {
        "starter": 0,
        "growth": 0,
        "premium": 0,
        "active_subscriptions": 0,
        "expiring_soon": 0,
        "expired": 0
    }
    if table_exists(cursor, "user_subscriptions"):
        try:
            cursor.execute("SELECT COUNT(DISTINCT user_id) as c FROM user_subscriptions WHERE status='active' AND end_date > NOW()")
            stats["subscription_stats"]["active_subscriptions"] = int(cursor.fetchone()["c"] or 0)
        except Exception:
            pass
        try:
            cursor.execute("SELECT COUNT(DISTINCT user_id) as c FROM user_subscriptions WHERE status='active' AND end_date <= DATE_ADD(NOW(), INTERVAL 7 DAY)")
            stats["subscription_stats"]["expiring_soon"] = int(cursor.fetchone()["c"] or 0)
        except Exception:
            pass
        try:
            cursor.execute("SELECT COUNT(DISTINCT user_id) as c FROM user_subscriptions WHERE (status != 'active' OR end_date <= NOW())")
            stats["subscription_stats"]["expired"] = int(cursor.fetchone()["c"] or 0)
        except Exception:
            pass
        try:
            cursor.execute("SELECT plan_name, COUNT(DISTINCT user_id) as c FROM user_subscriptions WHERE status='active' AND end_date > NOW() GROUP BY plan_name")
            for row in cursor.fetchall():
                plan_name = (row["plan_name"] or "").strip().lower()
                count = int(row["c"] or 0)
                if plan_name in ["starter", "basic"]:
                    stats["subscription_stats"]["starter"] += count
                elif plan_name in ["growth", "standard"]:
                    stats["subscription_stats"]["growth"] += count
                elif plan_name in ["pro", "premium"]:
                    stats["subscription_stats"]["premium"] += count
                else:
                    stats["subscription_stats"][plan_name] = stats["subscription_stats"].get(plan_name, 0) + count
        except Exception:
            pass

    # Boost performance stats
    stats["boost_stats"] = {
        "active_boosts": stats.get("boosted_ads_active", 0),
        "boosted_listings": 0,
        "boost_revenue": 0.0
    }
    if table_exists(cursor, "ad_boosts"):
        try:
            cursor.execute("SELECT COUNT(DISTINCT ad_id) as c FROM ad_boosts WHERE status='active' AND expiry_date > NOW()")
            stats["boost_stats"]["boosted_listings"] = int(cursor.fetchone()["c"] or 0)
        except Exception:
            pass
    elif table_exists(cursor, "boosted_listings"):
        try:
            cursor.execute("SELECT COUNT(DISTINCT listing_id) as c FROM boosted_listings WHERE status='active' AND end_date >= NOW()")
            stats["boost_stats"]["boosted_listings"] = int(cursor.fetchone()["c"] or 0)
        except Exception:
            pass
    if table_exists(cursor, "payments"):
        try:
            total_expr = get_payment_total_expression(cursor)
            status_filter = get_payment_status_filter()
            if column_exists(cursor, "payments", "type"):
                cursor.execute(f"SELECT COALESCE(SUM({total_expr}),0) as c FROM payments WHERE type='boost' AND {status_filter}")
            else:
                cursor.execute(f"SELECT COALESCE(SUM({total_expr}),0) as c FROM payments p JOIN ad_boosts b ON b.payment_id = p.id WHERE {status_filter}")
            stats["boost_stats"]["boost_revenue"] = float(cursor.fetchone()["c"] or 0)
        except Exception:
            stats["boost_stats"]["boost_revenue"] = 0.0

    # Listing status breakdown
    stats["listing_status_breakdown"] = {
        "active": stats.get("active_listings", 0),
        "sold": 0,
        "pending": 0
    }
    if table_exists(cursor, "listings"):
        try:
            cursor.execute("SELECT COUNT(*) as c FROM listings WHERE status='sold' OR approval_status='sold'")
            stats["listing_status_breakdown"]["sold"] = int(cursor.fetchone()["c"] or 0)
        except Exception:
            pass
        try:
            cursor.execute("SELECT COUNT(*) as c FROM listings WHERE approval_status='pending' OR status='pending'")
            stats["listing_status_breakdown"]["pending"] = int(cursor.fetchone()["c"] or 0)
        except Exception:
            pass

    # Smart insights
    stats["smart_insights"] = []
    if stats.get("revenue_growth", 0) < 0:
        stats["smart_insights"].append(f"Revenue dropped {abs(stats['revenue_growth'])}% compared to last month")
    else:
        stats["smart_insights"].append(f"Revenue increased {stats['revenue_growth']}% compared to last month")
    if stats.get("user_growth", 0) < 0:
        stats["smart_insights"].append(f"User growth is down {abs(stats['user_growth'])}% vs last week")
    else:
        stats["smart_insights"].append(f"User growth is up {stats['user_growth']}% vs last week")
    if stats.get("new_users_today", 0) == 0 and stats.get("total_users", 0) > 0:
        stats["smart_insights"].append("No new users registered today ⚠")
    if stats.get("active_users", 0) == 0 and stats.get("total_users", 0) > 0:
        stats["smart_insights"].append("No active users in the last 7 days ⚠")
    if stats.get("top_categories"):
        category_name = stats["top_categories"][0]["category"] if stats["top_categories"] else None
        if category_name:
            stats["smart_insights"].append(f"Most active category: {category_name}")

    # Ensure naming matches frontend conventions
    stats["totalUsers"] = stats["total_users"]
    stats["activeUsers"] = stats["active_users"]
    stats["newUsersToday"] = stats["new_users_today"]
    stats["totalListings"] = stats["total_listings"]
    stats["activeListings"] = stats["active_listings"]
    stats["boostedAds"] = stats["boosted_ads_active"]
    stats["revenueThisMonth"] = stats["revenue_month"]
    stats["revenueGrowth"] = stats["revenue_growth"]
    stats["userGrowth"] = stats["user_growth"]
    stats["revenueTrend"] = stats["revenue_trend"]
    stats["listingsTrend"] = stats["listings_growth_trend"]
    stats["subscriptionStats"] = stats["subscription_stats"]
    stats["boostStats"] = stats["boost_stats"]
    stats["topCategories"] = stats["top_categories"]
    stats["listingStatusBreakdown"] = stats["listing_status_breakdown"]
    stats["smartInsights"] = stats["smart_insights"]
    stats["usersTrend"] = stats.get("users_trend", [])

    return stats


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Render admin dashboard or return dashboard stats as JSON"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        wants_json = request.args.get("json") == "1" or 'application/json' in request.headers.get('Accept', '')
        if wants_json:
            stats = fetch_admin_dashboard_stats(cursor)
            return jsonify(stats)
        return render_template("admin/admin_dashboard.html")
    except Exception as e:
        current_app.logger.error(f"Error loading admin dashboard: {e}")
        if request.args.get("json") == "1":
            return jsonify({"error": "Unable to load dashboard data"}), 500
        flash(f"❌ Error loading dashboard: {str(e)}", "error")
        return redirect(url_for("home"))
    finally:
        cursor.close()
        conn.close()

@admin_bp.route("/api/dashboard")
@admin_required
def dashboard_api():
    """Return JSON dashboard metrics for admin pages."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        stats = fetch_admin_dashboard_stats(cursor)
        return jsonify(stats)
    except Exception as e:
        current_app.logger.error(f"Error returning admin dashboard JSON: {e}")
        return jsonify({"error": "Unable to load dashboard data"}), 500
    finally:
        cursor.close()
        conn.close()

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
        # Sync any active ad_boosts into boosted_listings so admin can see them
        try:
            cur.execute("""
                INSERT INTO boosted_listings (listing_id, seller_id, boost_type, start_date, end_date, status, created_at)
                SELECT b.ad_id, b.user_id,
                       COALESCE(bp.boost_type, 'standard'),
                       b.start_date, b.expiry_date, 'active', b.created_at
                FROM ad_boosts b
                LEFT JOIN boosted_listings bl
                    ON bl.listing_id = b.ad_id
                    AND bl.seller_id = b.user_id
                    AND bl.start_date = b.start_date
                    AND bl.end_date = b.expiry_date
                LEFT JOIN boost_packages bp ON b.package_id = bp.id
                WHERE b.status = 'active'
                  AND b.expiry_date > NOW()
                  AND bl.id IS NULL
            """)
            conn.commit()
        except Exception as sync_err:
            current_app.logger.warning(f"Could not sync active ad_boosts to boosted_listings: {sync_err}")

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
        current_app.logger.error(f"Error fetching boosted listings: {e}")
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

@admin_bp.route("/subscriptions")
@admin_required
def manage_subscriptions():
    """List seller subscription records for admin review."""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', 'all')
        search = request.args.get('search', '')
        items_per_page = 12

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        where_clauses = []
        params = []

        if status_filter == 'active':
            where_clauses.append("us.status = 'active' AND us.end_date > NOW()")
        elif status_filter == 'expired':
            where_clauses.append("(us.status = 'expired' OR us.end_date <= NOW())")
        elif status_filter == 'expiring':
            where_clauses.append("us.status = 'active' AND us.end_date <= DATE_ADD(NOW(), INTERVAL 7 DAY)")

        if search:
            where_clauses.append("(u.username LIKE %s OR u.email LIKE %s OR us.plan_name LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        where_sql = ' WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''

        count_query = "SELECT COUNT(*) as total FROM user_subscriptions us LEFT JOIN users u ON u.id = us.user_id" + where_sql
        cur.execute(count_query, tuple(params))
        count_row = cur.fetchone()
        total = count_row['total'] if count_row else 0

        offset = (page - 1) * items_per_page
        cur.execute(f"""
            SELECT us.id, us.user_id, u.username, u.email, us.plan_name, us.ad_limit, us.ads_used, 
                   us.start_date, us.end_date, us.status,
                   (SELECT st.amount FROM subscription_transactions st 
                    WHERE st.user_id = us.user_id AND st.plan_name = us.plan_name 
                      AND st.created_at <= us.start_date 
                    ORDER BY st.created_at DESC LIMIT 1) as amount_paid
            FROM user_subscriptions us
            LEFT JOIN users u ON u.id = us.user_id
            {where_sql}
            ORDER BY us.start_date DESC
            LIMIT %s OFFSET %s
        """, tuple(params + [items_per_page, offset]))
        subscriptions = cur.fetchall()

        for sub in subscriptions:
            sub['amount_paid'] = float(sub['amount_paid'] or 0)
            sub['is_active'] = (sub['status'] == 'active' and sub['end_date'] and sub['end_date'] > datetime.now())
            sub['is_expired'] = (sub['status'] != 'active' or (sub['end_date'] and sub['end_date'] <= datetime.now()))

        total_pages = (total + items_per_page - 1) // items_per_page

        cur.close()
        conn.close()

        return render_template("admin/admin_subscriptions.html",
                             subscriptions=subscriptions,
                             total=total,
                             status_filter=status_filter,
                             search=search,
                             total_pages=total_pages,
                             current_page=page)
    except Exception as e:
        flash(f"❌ Error loading subscriptions: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route("/user/<int:user_id>/subscription/<int:subscription_id>/extend", methods=["POST"])
@admin_required
def extend_subscription(user_id, subscription_id):
    try:
        from subscription_helpers import extend_user_subscription
        success = extend_user_subscription(user_id, subscription_id, 30)
        if success:
            flash("✅ Subscription extended by 30 days", "success")
        else:
            flash("❌ Could not extend subscription", "error")
    except Exception as e:
        flash(f"❌ Error extending subscription: {str(e)}", "error")
    return redirect(url_for("admin.manage_subscriptions"))

@admin_bp.route("/user/<int:user_id>/subscription/<int:subscription_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_subscription(user_id, subscription_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE user_subscriptions SET status='expired', end_date=NOW() WHERE id=%s AND user_id=%s", (subscription_id, user_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("✅ Subscription deactivated successfully", "success")
    except Exception as e:
        flash(f"❌ Error deactivating subscription: {str(e)}", "error")
    return redirect(url_for("admin.manage_subscriptions"))

@admin_bp.route("/user/<int:user_id>/subscription/<int:subscription_id>/activate", methods=["POST"])
@admin_required
def activate_subscription(user_id, subscription_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE user_subscriptions SET status='active', start_date=NOW(), end_date=DATE_ADD(NOW(), INTERVAL 30 DAY) WHERE id=%s AND user_id=%s", (subscription_id, user_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("✅ Subscription activated successfully", "success")
    except Exception as e:
        flash(f"❌ Error activating subscription: {str(e)}", "error")
    return redirect(url_for("admin.manage_subscriptions"))

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

def ensure_transactions_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            type ENUM('subscription','boost') NOT NULL,
            reference_id INT NULL,
            base_amount DECIMAL(10,2) NOT NULL,
            gst_amount DECIMAL(10,2) NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            payment_method ENUM('UPI','Card','Wallet') NOT NULL,
            status ENUM('completed','failed','refunded') NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_transactions_status (status),
            INDEX idx_transactions_type (type),
            INDEX idx_transactions_payment_method (payment_method),
            INDEX idx_transactions_created_at (created_at)
        )
    """)


def build_transaction_filters(args, exclude_month=False):
    filters = {
        'month': args.get('month', ''),
        'payment_method': args.get('payment_method', ''),
        'type': args.get('type', ''),
        'status': args.get('status', '')
    }
    clauses = []
    params = []

    if filters['month'] and not exclude_month:
        clauses.append("DATE_FORMAT(t.created_at, '%b %Y') = %s")
        params.append(filters['month'])
    if filters['payment_method']:
        clauses.append("t.payment_method = %s")
        params.append(filters['payment_method'])
    if filters['type'] in ['subscription', 'boost']:
        clauses.append("t.type = %s")
        params.append(filters['type'])
    if filters['status'] in ['completed', 'failed', 'refunded']:
        clauses.append("t.status = %s")
        params.append(filters['status'])
    else:
        clauses.append("t.status = 'completed'")

    where_sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    return where_sql, tuple(params), filters


def migrate_legacy_transactions(cursor):
    if not table_exists(cursor, 'transactions'):
        ensure_transactions_table(cursor)

    cursor.execute("SELECT COUNT(*) as count FROM transactions")
    existing_count = int(cursor.fetchone().get('count') or 0)
    if existing_count > 0:
        return

    if table_exists(cursor, 'payments'):
        cursor.execute("""
            SELECT p.id, p.user_id, p.amount, p.gst, p.total_amount, p.method, p.status,
                   p.created_at, b.id AS boost_id, st.id AS subscription_id,
                   COALESCE(st.payment_method, p.method) AS st_payment_method,
                   COALESCE(st.payment_status, p.status) AS st_payment_status
            FROM payments p
            LEFT JOIN ad_boosts b ON b.payment_id = p.id
            LEFT JOIN subscription_transactions st ON st.transaction_id = p.transaction_id AND st.user_id = p.user_id
        """)
        for row in cursor.fetchall():
            tx_type = 'boost' if row.get('boost_id') else 'subscription' if row.get('subscription_id') else None
            if not tx_type:
                continue
            reference_id = row.get('boost_id') or row.get('subscription_id')
            base_amount = row.get('amount')
            if base_amount is None:
                if row.get('total_amount') is not None and row.get('gst') is not None:
                    base_amount = float(row['total_amount']) - float(row['gst'])
                else:
                    base_amount = float(row.get('total_amount') or 0)
            gst_amount = float(row['gst']) if row.get('gst') is not None else calculate_gst(base_amount)
            payment_method = map_payment_method(row.get('method') or row.get('st_payment_method'))
            status = map_transaction_status(row.get('status') or row.get('st_payment_status'))
            total_amount = float(row['total_amount']) if row.get('total_amount') is not None else calculate_total(base_amount)
            cursor.execute("""
                INSERT INTO transactions (user_id, type, reference_id, base_amount, gst_amount, total_amount, payment_method, status, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                row['user_id'], tx_type, reference_id, float(base_amount), gst_amount, total_amount, payment_method, status, row['created_at']
            ))

    if table_exists(cursor, 'subscription_transactions'):
        cursor.execute("""
            SELECT st.id, st.user_id, st.amount, st.payment_method, st.payment_status, st.created_at
            FROM subscription_transactions st
            LEFT JOIN payments p ON p.transaction_id = st.transaction_id AND p.user_id = st.user_id
            WHERE p.id IS NULL
        """)
        for row in cursor.fetchall():
            base_amount = row.get('amount') or 0
            gst_amount = calculate_gst(base_amount)
            payment_method = map_payment_method(row.get('payment_method'))
            status = map_transaction_status(row.get('payment_status'))
            total_amount = calculate_total(base_amount)
            cursor.execute("""
                INSERT INTO transactions (user_id, type, reference_id, base_amount, gst_amount, total_amount, payment_method, status, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                row['user_id'], 'subscription', row['id'], float(base_amount), gst_amount, total_amount, payment_method, status, row['created_at']
            ))


def fetch_transactions_stats(cursor, where_sql, params):
    cursor.execute(f"SELECT COUNT(*) as count, COALESCE(SUM(total_amount),0) as total, COALESCE(AVG(total_amount),0) as avg_amount FROM transactions t {where_sql}", params)
    row = cursor.fetchone() or {}
    if where_sql:
        month_sql = f"SELECT COALESCE(SUM(total_amount),0) as month_total FROM transactions t {where_sql} AND YEAR(t.created_at)=YEAR(NOW()) AND MONTH(t.created_at)=MONTH(NOW())"
        month_params = params
    else:
        month_sql = "SELECT COALESCE(SUM(total_amount),0) as month_total FROM transactions t WHERE YEAR(t.created_at)=YEAR(NOW()) AND MONTH(t.created_at)=MONTH(NOW())"
        month_params = ()
    cursor.execute(month_sql, month_params)
    month_row = cursor.fetchone() or {}
    total = float(row.get('total') or 0)
    month_total = float(month_row.get('month_total') or 0)
    count = int(row.get('count') or 0)
    avg_amount = float(row.get('avg_amount') or 0)
    return {
        'total_revenue': total,
        'monthly_revenue': month_total,
        'total_transactions': count,
        'avg_transaction': avg_amount,
        'totalRevenue': total,
        'monthlyRevenue': month_total,
        'totalTransactions': count,
        'avgTransaction': avg_amount
    }


def fetch_transactions_rows(cursor, where_sql, params, limit=200):
    joins = []
    has_subscription_transactions = table_exists(cursor, 'subscription_transactions')
    has_ad_boosts = table_exists(cursor, 'ad_boosts')
    has_boost_packages = table_exists(cursor, 'boost_packages')
    has_listings = table_exists(cursor, 'listings')

    if has_subscription_transactions:
        joins.append("LEFT JOIN subscription_transactions st ON t.type='subscription' AND t.reference_id = st.id")
    if has_ad_boosts:
        joins.append("LEFT JOIN ad_boosts b ON t.type='boost' AND t.reference_id = b.id")
    if has_boost_packages and has_ad_boosts:
        joins.append("LEFT JOIN boost_packages bp ON b.package_id = bp.id")
    if has_listings and has_ad_boosts:
        joins.append("LEFT JOIN listings l ON b.ad_id = l.id")

    join_sql = '\n        '.join(joins)

    query = f"""
        SELECT
            t.id,
            t.user_id,
            u.username AS name,
            u.email,
            t.type,
            t.reference_id,
            t.base_amount,
            t.gst_amount,
            t.total_amount,
            t.payment_method,
            t.status,
            t.created_at,
            COALESCE(
                CASE WHEN t.type='subscription' THEN st.plan_name END,
                CASE WHEN t.type='boost' THEN bp.name END,
                CONCAT(UPPER(t.type), ' Transaction')
            ) as plan_name,
            CASE WHEN t.type='boost' THEN COALESCE(b.status, 'unknown') ELSE 'N/A' END as promotion_status,
            COALESCE(l.status, l.approval_status, 'N/A') as listing_status,
            COALESCE(l.title, 'Unknown Listing') as listing_title
        FROM transactions t
        LEFT JOIN users u ON u.id = t.user_id
        {join_sql}
        {where_sql}
        ORDER BY t.created_at DESC
        LIMIT {limit}
    """
    cursor.execute(query, params)
    rows = cursor.fetchall()
    output = []
    for row in rows:
        output.append({
            'id': row['id'],
            'user_name': row.get('name') or 'Unknown',
            'user_email': row.get('email') or '',
            'type': row['type'],
            'plan_name': row.get('plan_name') or 'Unknown',
            'base_amount': float(row.get('base_amount') or 0),
            'gst_amount': float(row.get('gst_amount') or 0),
            'total_amount': float(row.get('total_amount') or 0),
            'payment_method': row.get('payment_method') or 'Unknown',
            'promotion_status': row.get('promotion_status') or 'N/A',
            'listing_status': row.get('listing_status') or 'N/A',
            'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
            'date': row.get('created_at').isoformat() if row.get('created_at') else None,
            'status': row.get('status') or 'unknown',
            'listing_title': row.get('listing_title') or 'N/A',
            'reference_id': row.get('reference_id')
        })
    return output


def fetch_transaction_charts(cursor, where_sql, params):
    charts = {
        'monthlyRevenue': [],
        'paymentMethods': [],
        'revenueByType': []
    }

    cursor.execute(f"""
        SELECT DATE_FORMAT(created_at, '%b %Y') as period, COALESCE(SUM(total_amount),0) as total
        FROM transactions t
        {where_sql}
        GROUP BY DATE_FORMAT(created_at, '%b %Y')
        ORDER BY MIN(created_at) DESC
        LIMIT 12
    """, params)
    rows = cursor.fetchall()
    charts['monthlyRevenue'] = [
        {'label': row['period'], 'value': float(row['total'] or 0)}
        for row in rows
    ]

    cursor.execute(f"""
        SELECT payment_method, COUNT(*) as count
        FROM transactions t
        {where_sql}
        GROUP BY payment_method
    """, params)
    rows = cursor.fetchall()
    charts['paymentMethods'] = [
        {'method': row['payment_method'] or 'Unknown', 'count': int(row['count'] or 0)}
        for row in rows
    ]

    cursor.execute(f"""
        SELECT type, COALESCE(SUM(total_amount),0) as total
        FROM transactions t
        {where_sql}
        GROUP BY type
    """, params)
    rows = cursor.fetchall()
    charts['revenueByType'] = [
        {'type': row['type'] or 'Unknown', 'total': float(row['total'] or 0)}
        for row in rows
    ]

    return charts


def available_transaction_filters(cursor):
    months = []
    if table_exists(cursor, 'transactions'):
        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%b %Y') as ym
            FROM transactions
            GROUP BY ym
            ORDER BY MAX(created_at) DESC
        """)
        months = [row['ym'] for row in cursor.fetchall()]
    return {
        'months': months,
        'payment_methods': ['UPI', 'Card', 'Wallet'],
        'types': ['subscription', 'boost'],
        'statuses': ['completed', 'failed', 'refunded']
    }


def compute_filtered_transactions(cursor, args):
    where_sql, params, filters = build_transaction_filters(args)
    stats = fetch_transactions_stats(cursor, where_sql, params)
    transactions = fetch_transactions_rows(cursor, where_sql, params)
    charts = fetch_transaction_charts(cursor, where_sql, params)
    return {
        'success': True,
        'stats': stats,
        'transactions': transactions,
        'charts': charts,
        'filters': available_transaction_filters(cursor),
        'applied_filters': filters
    }


@admin_bp.route("/revenue")
@admin_required
def revenue():
    return render_template("admin/admin_payments.html")


@admin_bp.route("/transactions")
@admin_required
def transactions_api():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        if not table_exists(cur, 'transactions'):
            ensure_transactions_table(cur)
        migrate_legacy_transactions(cur)
        conn.commit()
        response = compute_filtered_transactions(cur, request.args)
        cur.close()
        conn.close()
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Error loading transactions API: {e}")
        return jsonify({'success': False, 'message': 'Unable to load transactions'}), 500


@admin_bp.route("/revenue-stats")
@admin_required
def revenue_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        if not table_exists(cur, 'transactions'):
            ensure_transactions_table(cur)
        migrate_legacy_transactions(cur)
        conn.commit()
        where_sql, params, _ = build_transaction_filters(request.args)
        stats = fetch_transactions_stats(cur, where_sql, params)
        cur.close()
        conn.close()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        current_app.logger.error(f"Error loading revenue stats: {e}")
        return jsonify({'success': False, 'message': 'Unable to load revenue stats'}), 500


@admin_bp.route("/transactions/refund/<int:transaction_id>", methods=["POST"])
@admin_required
def refund_transaction(transaction_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        if not table_exists(cur, 'transactions'):
            return jsonify({'success': False, 'message': 'Transactions table not found'}), 404

        cur.execute("SELECT * FROM transactions WHERE id=%s", (transaction_id,))
        tx = cur.fetchone()
        if not tx:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Transaction not found'}), 404

        if tx['status'] == 'refunded':
            cur.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Transaction already refunded'})

        cur.execute("UPDATE transactions SET status='refunded' WHERE id=%s", (transaction_id,))
        if tx['type'] == 'boost' and tx['reference_id']:
            cur.execute("UPDATE ad_boosts SET status='refunded' WHERE id=%s", (tx['reference_id'],))
            cur.execute("UPDATE payments p JOIN ad_boosts b ON b.payment_id = p.id SET p.status='refunded' WHERE b.id=%s", (tx['reference_id'],))
        elif tx['type'] == 'subscription' and tx['reference_id']:
            cur.execute("UPDATE subscription_transactions SET payment_status='refunded' WHERE id=%s", (tx['reference_id'],))
            cur.execute("UPDATE payments p JOIN subscription_transactions st ON p.transaction_id = st.transaction_id SET p.status='refunded' WHERE st.id=%s", (tx['reference_id'],))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Transaction refunded successfully'})
    except Exception as e:
        current_app.logger.error(f"Error refunding transaction: {e}")
        return jsonify({'success': False, 'message': 'Refund failed'}), 500

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
        # KPI counts
        try:
            cur.execute("SELECT COUNT(*) as c FROM users WHERE role!='admin'")
            total_users = int(cur.fetchone()["c"] or 0)
        except Exception:
            total_users = 0
        try:
            cur.execute("SELECT COUNT(*) as c FROM listings")
            total_listings = int(cur.fetchone()["c"] or 0)
        except Exception:
            total_listings = 0
        try:
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='active'")
            active_listings = int(cur.fetchone()["c"] or 0)
        except Exception:
            active_listings = 0
        # Active sellers: active listing OR active boost OR active subscription
        try:
            cur.execute("""
                SELECT COUNT(DISTINCT user_id) as c FROM (
                    SELECT user_id FROM listings WHERE status='active'
                    UNION
                    SELECT user_id FROM ad_boosts WHERE status='active' AND expiry_date > NOW()
                    UNION
                    SELECT user_id FROM user_subscriptions WHERE status='active' AND end_date > NOW()
                ) t
            """)
            active_sellers = int(cur.fetchone()["c"] or 0)
        except Exception:
            active_sellers = 0
        try:
            cur.execute("SELECT COUNT(DISTINCT user_id) as c FROM listings")
            total_sellers = int(cur.fetchone()["c"] or 0)
        except Exception:
            total_sellers = 0
        # Revenue from successful transactions only
        try:
            if table_exists(cur, 'transactions'):
                cur.execute("SELECT COALESCE(SUM(total_amount),0) as s FROM transactions WHERE status='completed'")
                total_revenue = float(cur.fetchone()["s"] or 0)
            else:
                total_expr = get_payment_total_expression(cur)
                status_filter = get_payment_status_filter()
                cur.execute(f"SELECT COALESCE(SUM({total_expr}),0) as s FROM payments WHERE {status_filter}")
                total_revenue = float(cur.fetchone()["s"] or 0)
        except Exception:
            total_revenue = 0.0
        try:
            if table_exists(cur, 'transactions'):
                cur.execute("SELECT COALESCE(SUM(total_amount),0) as s FROM transactions WHERE type='boost' AND status='completed'")
                boost_revenue = float(cur.fetchone()["s"] or 0)
            else:
                total_expr = get_payment_total_expression(cur)
                status_filter = get_payment_status_filter()
                if column_exists(cur, "payments", "type"):
                    cur.execute(f"SELECT COALESCE(SUM({total_expr}),0) as s FROM payments WHERE type='boost' AND {status_filter}")
                else:
                    cur.execute(f"""
                        SELECT COALESCE(SUM({total_expr}),0) as s
                        FROM payments p
                        JOIN ad_boosts b ON b.payment_id = p.id
                        WHERE {status_filter}
                    """)
                boost_revenue = float(cur.fetchone()["s"] or 0)
        except Exception:
            boost_revenue = 0.0
        try:
            if table_exists(cur, 'transactions'):
                cur.execute("SELECT COALESCE(SUM(total_amount),0) as s FROM transactions WHERE type='subscription' AND status='completed'")
                subscription_revenue = float(cur.fetchone()["s"] or 0)
            else:
                total_expr = get_payment_total_expression(cur)
                status_filter = get_payment_status_filter()
                if column_exists(cur, "payments", "type"):
                    cur.execute(f"SELECT COALESCE(SUM({total_expr}),0) as s FROM payments WHERE type='subscription' AND {status_filter}")
                else:
                    cur.execute(f"""
                        SELECT COALESCE(SUM({total_expr}),0) as s
                        FROM payments p
                        LEFT JOIN subscription_transactions st ON st.transaction_id = p.transaction_id AND st.user_id = p.user_id
                        WHERE {status_filter}
                          AND st.id IS NOT NULL
                    """)
                subscription_revenue = float(cur.fetchone()["s"] or 0)
        except Exception:
            subscription_revenue = 0.0
        # New users in last 7 days
        try:
            cur.execute("SELECT COUNT(*) as c FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            new_users_week = int(cur.fetchone()["c"] or 0)
        except Exception:
            new_users_week = 0
        try:
            cur.execute("""
                SELECT
                  SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as this_wk,
                  SUM(CASE WHEN created_at < DATE_SUB(NOW(), INTERVAL 7 DAY) AND created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY) THEN 1 ELSE 0 END) as prev_wk
                FROM users
            """)
            r = cur.fetchone()
            prev_week = int(r["prev_wk"] or 0)
            new_users_week_delta = new_users_week - prev_week
        except Exception:
            new_users_week_delta = 0
        # Revenue by month for chart
        rev_labels, rev_values = [], []
        try:
            total_expr = get_payment_total_expression(cur)
            status_filter = get_payment_status_filter()
            cur.execute(f"""
                SELECT DATE_FORMAT(created_at,'%b %Y') as ym, SUM({total_expr}) as amt, MIN(created_at) as d
                FROM payments
                WHERE {status_filter}
                GROUP BY DATE_FORMAT(created_at,'%Y-%m')
                ORDER BY MIN(created_at) ASC
                LIMIT 12
            """)
            rows = cur.fetchall()
            rev_labels = [r["ym"] for r in rows]
            rev_values = [float(r["amt"] or 0) for r in rows]
        except Exception:
            pass
        revenue_growth_pct = 0
        if len(rev_values) >= 2:
            prev = rev_values[-2] or 0
            curr = rev_values[-1] or 0
            revenue_growth_pct = int(((curr - prev) / prev) * 100) if prev else (100 if curr > 0 else 0)
        # Listings over last 14 days
        lst_day_labels, lst_day_counts = [], []
        try:
            cur.execute("""
                SELECT DATE(created_at) as d, COUNT(*) as c
                FROM listings
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)
                GROUP BY DATE(created_at)
                ORDER BY d
            """)
            rows = cur.fetchall()
            lst_day_labels = [r["d"].strftime("%d %b") for r in rows]
            lst_day_counts = [int(r["c"] or 0) for r in rows]
        except Exception:
            pass
        # Active vs sold
        active_vs_sold = [0, 0]
        try:
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='active'")
            active_vs_sold[0] = int(cur.fetchone()["c"] or 0)
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='sold' OR approval_status='sold'")
            active_vs_sold[1] = int(cur.fetchone()["c"] or 0)
        except Exception:
            pass
        # Category breakdown
        cat_labels, cat_counts = [], []
        try:
            cur.execute("""
                SELECT category, COUNT(*) as c
                FROM listings
                WHERE category IS NOT NULL AND category <> ''
                GROUP BY category
                ORDER BY c DESC
                LIMIT 10
            """)
            rows = cur.fetchall()
            cat_labels = [r["category"] for r in rows if r["category"]]
            cat_counts = [int(r["c"] or 0) for r in rows if r["category"]]
        except Exception:
            pass
        top_category = ""
        top_category_count = 0
        top_category_percentage = 0
        try:
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
            total_recent_listings = int(cur.fetchone()["c"] or 0)
            cur.execute("""
                SELECT category, COUNT(*) as c
                FROM listings
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                  AND category IS NOT NULL
                  AND category <> ''
                GROUP BY category
                ORDER BY c DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                top_category = row["category"] or ""
                top_category_count = int(row["c"] or 0)
                top_category_percentage = int((top_category_count / total_recent_listings) * 100) if total_recent_listings else 0
        except Exception:
            top_category = ""
            top_category_count = 0
            top_category_percentage = 0
        # Average listing price
        avg_listing_price = 0.0
        try:
            cur.execute("""
                SELECT
                  COUNT(*) as c,
                  COALESCE(SUM(CAST(price AS DECIMAL(12,2))),0) as s
                FROM listings
                WHERE price IS NOT NULL
                  AND price <> ''
                  AND (price + 0) > 0
            """)
            row = cur.fetchone()
            total_price_items = int(row["c"] or 0)
            total_price_sum = float(row["s"] or 0)
            avg_listing_price = round(total_price_sum / total_price_items, 2) if total_price_items else 0.0
        except Exception:
            avg_listing_price = 0.0
        # User growth daily
        usr_day_labels, usr_day_counts = [], []
        try:
            cur.execute("""
                SELECT DATE(created_at) as d, COUNT(*) as c
                FROM users
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)
                GROUP BY DATE(created_at)
                ORDER BY d
            """)
            rows = cur.fetchall()
            usr_day_labels = [r["d"].strftime("%d %b") for r in rows]
            usr_day_counts = [int(r["c"] or 0) for r in rows]
        except Exception:
            pass
        # New users this month/year
        try:
            cur.execute("SELECT COUNT(*) as c FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
            new_users_this_month = int(cur.fetchone()["c"] or 0)
        except Exception:
            new_users_this_month = 0
        try:
            cur.execute("SELECT COUNT(*) as c FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)")
            new_users_this_year = int(cur.fetchone()["c"] or 0)
        except Exception:
            new_users_this_year = 0
        # Health metrics
        listing_completion_rate = 0
        user_engagement_rate = 0
        boost_usage_pct = 0
        active_users_7d = 0
        try:
            cur.execute("""
                SELECT COUNT(*) as total,
                  SUM(CASE WHEN COALESCE(title,'') <> ''
                            AND COALESCE(description,'') <> ''
                            AND price IS NOT NULL
                            AND (price + 0) > 0
                            AND COALESCE(category,'') <> ''
                            AND COALESCE(location,'') <> '' THEN 1 ELSE 0 END) as complete
                FROM listings
            """)
            row = cur.fetchone()
            total_l = int(row["total"] or 0)
            complete_l = int(row["complete"] or 0)
            listing_completion_rate = int((complete_l / total_l) * 100) if total_l else 0
        except Exception:
            pass
        try:
            cur.execute("SELECT COUNT(*) as c FROM messages WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            msg7 = int(cur.fetchone()["c"] or 0)
            cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='active'")
            act = int(cur.fetchone()["c"] or 0)
            user_engagement_rate = min(100, int((msg7 / max(act,1)) * 20))
        except Exception:
            pass
        try:
            cur.execute("SELECT COUNT(DISTINCT ad_id) as c FROM ad_boosts WHERE status='active' AND expiry_date > NOW()")
            boosts_total = int(cur.fetchone()["c"] or 0)
        except Exception:
            boosts_total = 0
        try:
            boost_usage_pct = int((boosts_total / total_listings) * 100) if total_listings else 0
        except Exception:
            boost_usage_pct = 0
        try:
            cur.execute("""
                SELECT COUNT(DISTINCT user_id) as c FROM (
                    SELECT user_id FROM listings WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    UNION ALL
                    SELECT sender_id as user_id FROM messages WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ) t
            """)
            active_users_7d = int(cur.fetchone()["c"] or 0)
        except Exception:
            active_users_7d = 0
        # Boosted ads performance
        boosts_revenue = 0.0
        boosted_cat_labels, boosted_cat_counts = [], []
        try:
            cur.execute("SELECT COUNT(DISTINCT ad_id) as c FROM ad_boosts WHERE status='active' AND expiry_date > NOW()")
            boosts_total = int(cur.fetchone()["c"] or 0)
        except Exception:
            boosts_total = 0
        try:
            cur.execute("SELECT COALESCE(SUM(total_amount),0) as s FROM payments WHERE type='boost' AND status='success'")
            boosts_revenue = float(cur.fetchone()["s"] or 0)
        except Exception:
            boosts_revenue = 0.0
        try:
            cur.execute("""
                SELECT l.category, COUNT(*) as c
                FROM ad_boosts b
                JOIN listings l ON b.ad_id = l.id
                WHERE b.status='active' AND b.expiry_date > NOW()
                GROUP BY l.category
                ORDER BY c DESC
                LIMIT 5
            """)
            rows = cur.fetchall()
            boosted_cat_labels = [r["category"] for r in rows if r["category"]]
            boosted_cat_counts = [int(r["c"] or 0) for r in rows if r["category"]]
        except Exception:
            boosted_cat_labels = []
            boosted_cat_counts = []
        # Churn rate for subscription users
        churn_rate = 0
        try:
            cur.execute("""
                SELECT COUNT(*) as churned
                FROM (
                    SELECT user_id,
                      MAX(CASE WHEN status='active' AND end_date > NOW() THEN 1 ELSE 0 END) as has_active,
                      MAX(end_date) as last_end
                    FROM user_subscriptions
                    GROUP BY user_id
                ) t
                WHERE has_active = 0 AND last_end <= NOW()
            """)
            churned_users = int(cur.fetchone()["churned"] or 0)
            cur.execute("SELECT COUNT(DISTINCT user_id) as total FROM user_subscriptions")
            total_subscribed_users = int(cur.fetchone()["total"] or 0)
            churn_rate = int((churned_users / total_subscribed_users) * 100) if total_subscribed_users else 0
        except Exception:
            churn_rate = 0
        # Subscription mix by active plan
        subscription_mix = {"basic": 0, "standard": 0, "premium": 0}
        try:
            cur.execute("""
                SELECT plan_name, COUNT(DISTINCT user_id) as c
                FROM user_subscriptions
                WHERE status='active' AND end_date > NOW()
                GROUP BY plan_name
            """)
            for r in cur.fetchall():
                plan = (r["plan_name"] or "").lower()
                if plan == 'starter' or plan == 'basic':
                    subscription_mix['basic'] = int(r['c'] or 0)
                elif plan == 'growth' or plan == 'standard':
                    subscription_mix['standard'] = int(r['c'] or 0)
                elif plan == 'pro' or plan == 'premium':
                    subscription_mix['premium'] = int(r['c'] or 0)
        except Exception:
            subscription_mix = {"basic": 0, "standard": 0, "premium": 0}
        # Automatic insights
        auto_insights = []
        try:
            auto_insights.append(f"Revenue {'increased' if revenue_growth_pct >= 0 else 'decreased'} {abs(revenue_growth_pct)}% compared to last month")
            if top_category:
                auto_insights.append(f"'{top_category}' has the highest listings")
            if new_users_week_delta >= 0:
                auto_insights.append("User registrations increased this week")
            else:
                auto_insights.append("User registrations decreased this week")
        except Exception:
            pass
        # Recent activity
        recent = []
        try:
            cur.execute("SELECT 'user' as t, username as title, created_at FROM users ORDER BY created_at DESC LIMIT 5")
            recent += [{"type": "user", "title": r["title"], "created_at": r["created_at"].strftime("%d %b %H:%M")} for r in cur.fetchall()]
        except Exception:
            pass
        try:
            cur.execute("SELECT 'listing' as t, title, created_at FROM listings ORDER BY created_at DESC LIMIT 5")
            recent += [{"type": "listing", "title": r["title"], "created_at": r["created_at"].strftime("%d %b %H:%M")} for r in cur.fetchall()]
        except Exception:
            pass
        try:
            cur.execute("""
                SELECT 'boost' as t, CONCAT('Boost purchased for Ad #', ad_id) as title, created_at
                FROM payments WHERE type='boost' AND status='success'
                ORDER BY created_at DESC LIMIT 5
            """)
            recent += [{"type": "boost", "title": r["title"], "created_at": r["created_at"].strftime("%d %b %H:%M")} for r in cur.fetchall()]
        except Exception:
            pass
        insights = {
            "kpis": {
                "total_users": total_users,
                "total_listings": total_listings,
                "active_listings": active_listings,
                "boosted_ads": boosts_total,
                "total_revenue": int(total_revenue),
                "new_users_week": new_users_week,
                "new_users_week_delta": new_users_week_delta
            },
            "active_sellers": active_sellers,
            "seller_activity_rate": int((active_sellers / total_sellers) * 100) if total_sellers else 0,
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
            "top_category_percentage": top_category_percentage,
            "user_day_labels": usr_day_labels,
            "user_day_counts": usr_day_counts,
            "new_users_this_week": new_users_week,
            "new_users_this_month": new_users_this_month,
            "new_users_this_year": new_users_this_year,
            "avg_users_per_day": int(sum(usr_day_counts) / max(len(usr_day_counts), 1)),
            "listing_completion_rate": listing_completion_rate,
            "user_engagement_rate": user_engagement_rate,
            "boost_usage_pct": boost_usage_pct,
            "active_users_7d": active_users_7d,
            "boosts_total": boosts_total,
            "boosts_revenue": int(boosts_revenue),
            "subscription_revenue": int(subscription_revenue),
            "boosted_cat_labels": boosted_cat_labels,
            "boosted_cat_counts": boosted_cat_counts,
            "auto_insights": auto_insights,
            "recent": recent,
            "subscription_mix": subscription_mix,
            "peak_revenue_day": "",
            "most_sold_category": "",
            "avg_listing_price": avg_listing_price,
            "churn_rate": churn_rate,
            "low_data": total_users < 50 or total_listings < 50
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
        current_app.logger.exception("Error loading admin products")
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
