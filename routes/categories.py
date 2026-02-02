"""
Category Management Backend Routes
Handles category CRUD operations, filter management, and API endpoints
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from functools import wraps
import mysql.connector
from datetime import datetime

# Define blueprint
categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

# Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shra@0303",
        database="regear_db"
    )

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "Please login first"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({"success": False, "message": "Admin access only"}), 403
        return f(*args, **kwargs)
    return decorated_function

# ===========================
# API ENDPOINTS (Public)
# ===========================

@categories_bp.route('/api/all', methods=['GET'])
def api_get_all_categories():
    """Get all active categories with subcategories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all categories
        cursor.execute("""
            SELECT id, name, slug, description, icon, color 
            FROM categories 
            WHERE is_active = 1 
            ORDER BY display_order
        """)
        categories = cursor.fetchall()
        
        result = {}
        for cat in categories:
            cat_id = cat['id']
            
            # Get subcategories
            cursor.execute("""
                SELECT id, name, slug, description 
                FROM sub_categories 
                WHERE category_id = %s AND is_active = 1 
                ORDER BY display_order
            """, (cat_id,))
            subcats = cursor.fetchall()
            
            result[cat['slug']] = {
                'id': cat_id,
                'name': cat['name'],
                'description': cat['description'],
                'icon': cat['icon'],
                'color': cat['color'],
                'subcategories': [
                    {'id': s['id'], 'name': s['name'], 'slug': s['slug']} 
                    for s in subcats
                ]
            }
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "data": result}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@categories_bp.route('/api/category/<slug>', methods=['GET'])
def api_get_category(slug):
    """Get single category with subcategories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, slug, description, icon, color 
            FROM categories 
            WHERE slug = %s AND is_active = 1
        """, (slug,))
        category = cursor.fetchone()
        
        if not category:
            return jsonify({"success": False, "message": "Category not found"}), 404
        
        cat_id = category['id']
        
        # Get subcategories
        cursor.execute("""
            SELECT id, name, slug, description 
            FROM sub_categories 
            WHERE category_id = %s AND is_active = 1 
            ORDER BY display_order
        """, (cat_id,))
        subcategories = cursor.fetchall()
        
        # Get filters for this category
        cursor.execute("""
            SELECT cf.id, ft.name, ft.slug, ft.type, cf.is_required, cf.display_order, cf.filter_config
            FROM category_filters cf
            JOIN filter_types ft ON cf.filter_type_id = ft.id
            WHERE cf.category_id = %s AND ft.is_active = 1
            ORDER BY cf.display_order
        """, (cat_id,))
        filters = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                'id': category['id'],
                'name': category['name'],
                'slug': category['slug'],
                'description': category['description'],
                'icon': category['icon'],
                'subcategories': subcategories,
                'filters': filters
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@categories_bp.route('/api/subcategory/<int:sub_cat_id>/filters', methods=['GET'])
def api_get_subcategory_filters(sub_cat_id):
    """Get filters for a specific subcategory"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get subcategory info
        cursor.execute("""
            SELECT id, name, category_id
            FROM sub_categories 
            WHERE id = %s AND is_active = 1
        """, (sub_cat_id,))
        subcat = cursor.fetchone()
        
        if not subcat:
            return jsonify({"success": False, "message": "Subcategory not found"}), 404
        
        # Get filters for this subcategory AND parent category
        cursor.execute("""
            SELECT DISTINCT cf.id, ft.id as filter_type_id, ft.name, ft.slug, ft.type, 
                   cf.is_required, cf.display_order, cf.filter_config
            FROM category_filters cf
            JOIN filter_types ft ON cf.filter_type_id = ft.id
            WHERE (cf.sub_category_id = %s OR cf.category_id = %s) 
            AND ft.is_active = 1
            ORDER BY cf.display_order
        """, (sub_cat_id, subcat['category_id']))
        filters = cursor.fetchall()
        
        # Get filter options
        filter_data = []
        for f in filters:
            cursor.execute("""
                SELECT option_value, option_label, display_order
                FROM filter_options
                WHERE filter_type_id = %s AND is_active = 1
                ORDER BY display_order
            """, (f['filter_type_id'],))
            options = cursor.fetchall()
            
            filter_info = dict(f)
            filter_info['options'] = options
            filter_data.append(filter_info)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                'subcategory': subcat,
                'filters': filter_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ===========================
# ADMIN MANAGEMENT ROUTES
# ===========================

@categories_bp.route('/admin/list', methods=['GET'])
@admin_required
def admin_list_categories():
    """Admin page: List all categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, slug, description, icon, is_active, display_order, created_at
            FROM categories
            ORDER BY display_order
        """)
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/admin_categories.html', categories=categories)
        
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for('admin.dashboard'))

@categories_bp.route('/admin/create', methods=['GET', 'POST'])
@admin_required
def admin_create_category():
    """Admin: Create new category"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            slug = request.form.get('slug', '').strip().lower()
            description = request.form.get('description', '').strip()
            icon = request.form.get('icon', '').strip()
            color = request.form.get('color', '#0066cc').strip()
            display_order = request.form.get('display_order', 999)
            
            if not name or not slug:
                flash("❌ Name and slug are required", "error")
                return redirect(url_for('categories.admin_create_category'))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if slug already exists
            cursor.execute("SELECT id FROM categories WHERE slug = %s", (slug,))
            if cursor.fetchone():
                flash("❌ Slug already exists", "error")
                cursor.close()
                conn.close()
                return redirect(url_for('categories.admin_create_category'))
            
            cursor.execute("""
                INSERT INTO categories (name, slug, description, icon, color, display_order)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, slug, description, icon, color, display_order))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f"✅ Category '{name}' created successfully", "success")
            return redirect(url_for('categories.admin_list_categories'))
            
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('categories.admin_create_category'))
    
    return render_template('admin/admin_category_form.html', mode='create')

@categories_bp.route('/admin/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(category_id):
    """Admin: Edit category"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            slug = request.form.get('slug', '').strip().lower()
            description = request.form.get('description', '').strip()
            icon = request.form.get('icon', '').strip()
            color = request.form.get('color', '#0066cc').strip()
            display_order = request.form.get('display_order', 999)
            is_active = int(request.form.get('is_active', 1))
            
            if not name or not slug:
                flash("❌ Name and slug are required", "error")
                return redirect(url_for('categories.admin_edit_category', category_id=category_id))
            
            # Check if slug already exists (for different category)
            cursor.execute("SELECT id FROM categories WHERE slug = %s AND id != %s", (slug, category_id))
            if cursor.fetchone():
                flash("❌ Slug already exists", "error")
                cursor.close()
                conn.close()
                return redirect(url_for('categories.admin_edit_category', category_id=category_id))
            
            cursor.execute("""
                UPDATE categories 
                SET name = %s, slug = %s, description = %s, icon = %s, color = %s, 
                    display_order = %s, is_active = %s
                WHERE id = %s
            """, (name, slug, description, icon, color, display_order, is_active, category_id))
            
            conn.commit()
            flash(f"✅ Category updated successfully", "success")
            cursor.close()
            conn.close()
            return redirect(url_for('categories.admin_list_categories'))
        
        # GET: Show edit form
        cursor.execute("""
            SELECT id, name, slug, description, icon, color, display_order, is_active
            FROM categories
            WHERE id = %s
        """, (category_id,))
        category = cursor.fetchone()
        
        if not category:
            flash("❌ Category not found", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('categories.admin_list_categories'))
        
        cursor.close()
        conn.close()
        
        return render_template('admin/admin_category_form.html', mode='edit', category=category)
        
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for('categories.admin_list_categories'))

@categories_bp.route('/admin/delete/<int:category_id>', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    """Admin: Delete category (with safety check)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if any listings use this category
        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE category_id = %s", (category_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            flash(f"❌ Cannot delete category with {count} listings. Please delete listings first.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('categories.admin_list_categories'))
        
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("✅ Category deleted successfully", "success")
        return redirect(url_for('categories.admin_list_categories'))
        
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for('categories.admin_list_categories'))

# ===========================
# SUB-CATEGORIES MANAGEMENT
# ===========================

@categories_bp.route('/admin/subcategories', methods=['GET'])
@admin_required
def admin_list_subcategories():
    """Admin page: List all subcategories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT sc.id, sc.name, sc.slug, sc.category_id, c.name as category_name, 
                   sc.is_active, sc.display_order
            FROM sub_categories sc
            JOIN categories c ON sc.category_id = c.id
            ORDER BY c.display_order, sc.display_order
        """)
        subcategories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/admin_subcategories.html', subcategories=subcategories)
        
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for('admin.dashboard'))

@categories_bp.route('/admin/subcategory/create', methods=['GET', 'POST'])
@admin_required
def admin_create_subcategory():
    """Admin: Create new subcategory"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            category_id = request.form.get('category_id', type=int)
            name = request.form.get('name', '').strip()
            slug = request.form.get('slug', '').strip().lower()
            description = request.form.get('description', '').strip()
            display_order = request.form.get('display_order', 999)
            
            if not category_id or not name or not slug:
                flash("❌ Category, name, and slug are required", "error")
                return redirect(url_for('categories.admin_create_subcategory'))
            
            # Check if slug already exists in this category
            cursor.execute(
                "SELECT id FROM sub_categories WHERE category_id = %s AND slug = %s",
                (category_id, slug)
            )
            if cursor.fetchone():
                flash("❌ Slug already exists in this category", "error")
                cursor.close()
                conn.close()
                return redirect(url_for('categories.admin_create_subcategory'))
            
            cursor.execute("""
                INSERT INTO sub_categories (category_id, name, slug, description, display_order)
                VALUES (%s, %s, %s, %s, %s)
            """, (category_id, name, slug, description, display_order))
            
            conn.commit()
            flash(f"✅ Subcategory '{name}' created successfully", "success")
            cursor.close()
            conn.close()
            return redirect(url_for('categories.admin_list_subcategories'))
        
        # GET: Show form with category options
        cursor.execute("SELECT id, name FROM categories WHERE is_active = 1 ORDER BY display_order")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('admin/admin_subcategory_form.html', mode='create', categories=categories)
        
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for('categories.admin_list_subcategories'))

@categories_bp.route('/admin/subcategory/edit/<int:subcategory_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_subcategory(subcategory_id):
    """Admin: Edit subcategory"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            slug = request.form.get('slug', '').strip().lower()
            description = request.form.get('description', '').strip()
            display_order = request.form.get('display_order', 999)
            is_active = int(request.form.get('is_active', 1))
            
            if not name or not slug:
                flash("❌ Name and slug are required", "error")
                return redirect(url_for('categories.admin_edit_subcategory', subcategory_id=subcategory_id))
            
            cursor.execute("""
                UPDATE sub_categories 
                SET name = %s, slug = %s, description = %s, display_order = %s, is_active = %s
                WHERE id = %s
            """, (name, slug, description, display_order, is_active, subcategory_id))
            
            conn.commit()
            flash("✅ Subcategory updated successfully", "success")
            cursor.close()
            conn.close()
            return redirect(url_for('categories.admin_list_subcategories'))
        
        # GET: Show edit form
        cursor.execute("SELECT * FROM sub_categories WHERE id = %s", (subcategory_id,))
        subcategory = cursor.fetchone()
        
        if not subcategory:
            flash("❌ Subcategory not found", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('categories.admin_list_subcategories'))
        
        cursor.execute("SELECT id, name FROM categories WHERE is_active = 1 ORDER BY display_order")
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/admin_subcategory_form.html', mode='edit', 
                             subcategory=subcategory, categories=categories)
        
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for('categories.admin_list_subcategories'))

@categories_bp.route('/admin/subcategory/delete/<int:subcategory_id>', methods=['POST'])
@admin_required
def admin_delete_subcategory(subcategory_id):
    """Admin: Delete subcategory (with safety check)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if any listings use this subcategory
        cursor.execute("SELECT COUNT(*) as count FROM listings WHERE sub_category_id = %s", (subcategory_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            flash(f"❌ Cannot delete subcategory with {count} listings.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('categories.admin_list_subcategories'))
        
        cursor.execute("DELETE FROM sub_categories WHERE id = %s", (subcategory_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("✅ Subcategory deleted successfully", "success")
        return redirect(url_for('categories.admin_list_subcategories'))
        
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for('categories.admin_list_subcategories'))

# ===========================
# FILTER MANAGEMENT
# ===========================

@categories_bp.route('/admin/category/<int:category_id>/filters', methods=['GET'])
@admin_required
def admin_category_filters(category_id):
    """Admin page: Manage filters for a category"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get category
        cursor.execute("SELECT id, name FROM categories WHERE id = %s", (category_id,))
        category = cursor.fetchone()
        
        if not category:
            flash("❌ Category not found", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('categories.admin_list_categories'))
        
        # Get assigned filters
        cursor.execute("""
            SELECT cf.id, ft.id as filter_id, ft.name, ft.slug, ft.type, cf.is_required, cf.display_order
            FROM category_filters cf
            JOIN filter_types ft ON cf.filter_type_id = ft.id
            WHERE cf.category_id = %s
            ORDER BY cf.display_order
        """, (category_id,))
        assigned_filters = cursor.fetchall()
        
        # Get all available filters
        cursor.execute("""
            SELECT id, name, slug, type FROM filter_types WHERE is_active = 1 ORDER BY name
        """)
        all_filters = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/admin_category_filters.html', 
                             category=category, 
                             assigned_filters=assigned_filters,
                             all_filters=all_filters)
        
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
        return redirect(url_for('categories.admin_list_categories'))

@categories_bp.route('/admin/category-filter/assign', methods=['POST'])
@admin_required
def admin_assign_filter():
    """Admin: Assign filter to category"""
    try:
        data = request.get_json()
        category_id = data.get('category_id', type=int)
        filter_type_id = data.get('filter_type_id', type=int)
        is_required = data.get('is_required', 0, type=int)
        display_order = data.get('display_order', 999, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if already assigned
        cursor.execute(
            "SELECT id FROM category_filters WHERE category_id = %s AND filter_type_id = %s",
            (category_id, filter_type_id)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Filter already assigned"}), 400
        
        cursor.execute("""
            INSERT INTO category_filters (category_id, filter_type_id, is_required, display_order)
            VALUES (%s, %s, %s, %s)
        """, (category_id, filter_type_id, is_required, display_order))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Filter assigned successfully"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@categories_bp.route('/admin/category-filter/remove/<int:category_filter_id>', methods=['POST'])
@admin_required
def admin_remove_filter(category_filter_id):
    """Admin: Remove filter from category"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM category_filters WHERE id = %s", (category_filter_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Filter removed successfully"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
