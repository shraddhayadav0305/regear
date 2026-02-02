# ReGear Copilot Instructions

## Project Overview

**ReGear** is a Flask-based classifieds marketplace for buying/selling second-hand electronics and goods. It features multi-role authentication (buyer/seller/admin), category-based listings, and a comprehensive admin dashboard.

**Architecture Stack:**
- Backend: Flask (Python) + MySQL
- Frontend: Jinja2 templates + Bootstrap 5 + Vanilla JavaScript
- Database: MySQL with hardcoded localhost connection (user: root, password: Shra@0303)
- Server: localhost:5000

---

## Critical System Patterns

### 1. **Authentication & Authorization Flow**

**Key Pattern:** Session-based with role decorators

```python
# Every protected route uses @login_required decorator
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session.get('user_id')
    role = session.get('role')  # 'buyer', 'seller', 'admin', or 'blocked'
```

**Session Keys Stored:**
- `session['user_id']` - User database ID
- `session['username']` - Display name
- `session['role']` - User role determining access level

**Password Hashing:** SHA-256 with salt (format: `salt$hash`). Function `verify_password()` handles both new hashed and legacy plaintext passwords for backward compatibility.

**Admin Access:** `@admin_required` decorator checks role=='admin' before allowing access.

### 2. **Database Connection Pattern**

**Critical Issue:** Connection hardcoded in multiple locations with raw SQL. No connection pooling.

```python
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="Shra@0303",
        database="regear_db"
    )
```

**Always close connections:** `cursor.close()` then `conn.close()` after each operation.

**Dictionary results:** Use `cursor(dictionary=True)` for SELECT queries returning multiple rows.

### 3. **Category System Architecture**

**Two-level hierarchy:** Main categories → Subcategories

**16 Main Categories:** Mobiles, Computers & Laptops, Cameras & Lenses, TVs/Video/Audio, Gaming, Kitchen/Appliances, Computer Accessories, Electronic Hardware, Cars, Properties, Jobs, Bikes, Commercial Vehicles, Furniture, Fashion, Books/Sports

**Data Flow:**
1. `/sell` → displays `categories.html` with all 16 categories fetched from `/api/categories` endpoint
2. User clicks category → navigates to `/subcategories?category=X`
3. `/subcategories` route renders `subcategories.html` with category-specific subcategories
4. User clicks subcategory → `POST /save-category` (saves to session)
5. Redirects to `/post-ad-form` with prefilled category fields in `addpost.html`

**Key Points:**
- Categories are hardcoded in `/api/categories` endpoint as a dictionary (not in database)
- Each category has 5-9 subcategories
- Subcategories saved to session: `session['selected_category']`, `session['selected_subcategory']`
- Categories page uses dynamic fetch: `fetch('/api/categories')` → displays with Font Awesome icons
- Search functionality filters categories by name/description in real-time

### 4. **Form Submission Patterns**

**Frontend Validation:** Basic HTML5 + custom JavaScript (length checks, required fields)

**Backend Validation:** 
- Duplicate email/username checks with database
- Field length validation (title: 80 chars max, description: 2000 chars max)
- Flash messages for all feedback (success/error)

**File Upload:** Photo handling in ad creation (max 5 files per ad, uploaded to unknown location - implementation incomplete)

### 5. **Error Handling**

**Global Error Handlers:**
- 404 → redirects to home
- 500 → flash "Server error!", redirects to home

**Per-route Pattern:** Wrap in try/except, flash error message, redirect to appropriate page

```python
try:
    # operation
    conn.commit()
    flash("✅ Operation successful", "success")
    return redirect(url_for("route_name"))
except Exception as e:
    flash(f"❌ Error: {str(e)}", "error")
    return redirect(url_for("fallback_route"))
```

---

## Key Routes & Their Purpose

### Authentication Routes
- `GET/POST /register` - Role-based registration (buyer/seller)
- `GET/POST /login` - Email+password authentication  
- `GET /logout` - Session clear + redirect
- `GET/POST /forgot-password`, `/reset-password` - Password recovery

### User Routes (Protected)
- `GET /dashboard` - Role-specific dashboard (template changes based on role)
- `GET /saved` - Placeholder for saved items
- `GET /orders` - Placeholder for buyer orders
- `GET /analytics` - Placeholder for seller analytics

### Listing Routes
- `GET /sell` - **Now:** Category selection page with all 16 categories (categories.html)
- `GET /subcategories?category=X` - **New:** Shows subcategories for selected category
- `POST /save-category` - Saves selected category/subcategory to session
- `GET/POST /post-ad-form` - Create new listing (renders addpost.html with prefilled category)
- `GET /my-listings` - View seller's own listings
- `GET /browse` - Browse all active listings
- `GET /listing/<id>` - Individual listing detail view

### Admin Routes (Require @admin_required)
- `GET /admin` - Admin dashboard with stats
- `GET /admin/users` - List all users
- `GET /admin/block/<user_id>` - Block user (sets role='blocked')
- `GET /admin/unblock/<user_id>` - Unblock user (resets to role='buyer')

### Utility Routes
- `GET /health` - Health check endpoint
- `GET /api/categories` - Returns all categories as JSON
- `GET /api/reverse-geocode` - Converts lat/lng to Indian city names

---

## Database Tables & Schemas

### `users` Table
```sql
id, role (ENUM), username, email, password, phone, created_at
```

### `listings` Table
```sql
id, user_id, category, subcategory, title, description, price, 
location, phone, email, condition, created_at, status
```

Status values: 'active', 'pending', 'sold', 'archived'

---

## Development Workflows

### Running the Application
```bash
python app.py
# Server starts at http://localhost:5000 with debug=True
```

### Testing Authentication
1. Register at `/register` with buyer/seller role
2. Database query: `SELECT * FROM users ORDER BY id DESC LIMIT 1`
3. Login at `/login` to set session variables

### Adding New Routes
1. Import required modules at top of app.py
2. Define route with appropriate decorators (`@login_required` or `@admin_required`)
3. Use `session.get()` for accessing user context
4. Always close database connections (pattern shown above)
5. Use `flash()` for user feedback, `redirect(url_for())` for navigation

### Template Patterns
- Admin templates extend `admin/admin_layout.html` with `{% block content %}`
- Other templates are standalone (no base template used)
- Bootstrap 5 classes heavily used; custom inline styles common
- Flash messages displayed via `{% with messages = get_flashed_messages(with_categories=true) %}`

---

## Known Incomplete/Placeholder Features

- ~~File upload storage for listing photos~~ (code exists, location still TBD)
- ~~`create_listing.html` template~~ **FIXED** - Now uses addpost.html
- Buyer saved items (route exists but returns flash redirect)
- Orders system (route exists but returns flash redirect)
- Analytics page (route exists but returns flash redirect)
- Real reverse-geocode uses hardcoded Indian cities, not actual geolocation

---

## Common Pitfalls to Avoid

1. **Database credentials:** Hardcoded in multiple places - refactor to environment variables
2. **No connection pooling:** Each route creates new connection - causes slowness under load
3. **SQL injection:** Uses parameterized queries (good), but manually build them in many routes
4. **Session data:** Relies on `selected_category`/`selected_subcategory` in session (fragile, can be cleared)
5. **Template inconsistency:** Some templates use layout.html, others standalone - no unified pattern
6. **Error messages:** Database errors sometimes exposed to users (show str(e))

---

## Extending the Codebase

**Adding a new feature?**
1. Consider if it needs user authentication (`@login_required`)
2. Plan database table changes (add migration pattern missing - manual SQL only)
3. Add route following existing try/except error pattern
4. Create template in `templates/` directory
5. Add to navbar/menu if user-facing

**Testing the feature:**
- Create fresh database record: `INSERT INTO ...`
- Verify response code: 200, 302 (redirect), 400/500 (error)
- Check flash messages display correctly
- Verify role-based access (admin vs buyer/seller)
