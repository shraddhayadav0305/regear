# Homepage Featured Listings & Category Browse - Implementation Guide

## Feature Overview

This implementation adds functionality to:
1. **Display approved listings on the homepage** - A "Featured Listings" section shows the 12 most recent approved listings
2. **Browse listings by category** - Users can filter listings by category on the browse page
3. **Search functionality** - Listings can be searched across title, description, and category

## Files Modified

### Backend (Python/Flask)

#### `app.py`

**1. Updated `home()` route (lines ~80-95)**
```python
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
```

**2. Updated `browse()` route (lines ~590-640)**
```python
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
```

**3. Fixed `health()` route (lines ~500-515)**
- Fixed undefined `db` variable error
- Now properly checks database connectivity

### Frontend (HTML/Templates)

#### `templates/homepg.html`

**1. Added Featured Listings Section** (after categories section, before footer)
- Displays 12 latest approved listings in a responsive grid
- Shows listing image, title, price, location, and date
- Includes "View Details" button linking to individual listing page
- Includes "Browse All Listings" button to go to browse page
- Features empty state message if no approved listings exist

**2. Added CSS Styles for Featured Listings**
- `.featured-listings-section` - Main container with gradient background
- `.featured-listings-grid` - Responsive grid layout (auto-fill columns)
- `.listing-card` - Individual listing card with hover effects
- `.listing-image` - Image container with lazy loading placeholder
- `.listing-badge` - Category/condition badge overlay
- `.listing-content` - Text content area inside card
- `.listing-price` - Price display styling
- `.listing-button` - View Details button styling
- `.browse-all-btn` - Browse All button styling

#### `templates/browse_listings.html`

**1. Updated Category Filter** (line ~360)
```django
<select id="categoryFilter" class="form-select form-select-sm" onchange="updateFilters()">
    <option value="">All Categories</option>
    {% for category in categories %}
        <option value="{{ category }}" {% if selected_category == category %}selected{% endif %}>{{ category }}</option>
    {% endfor %}
</select>
```
- Now uses `categories` list from backend instead of hardcoded options
- Highlights `selected_category` if filtering is active

**2. Updated JavaScript** (lines ~507-590)
- Category filter now triggers server-side reload with `?category=X` parameter
- Reset filters clears category and other filters
- Price, condition, and location filters continue to work client-side
- Sort functionality remains intact

## How It Works

### Publishing Workflow

1. **User Posts an Ad**
   - User navigates to `/sell`
   - Selects category and subcategory
   - Fills in listing details (title, description, price, photos, etc.)
   - Submits form → Listing is saved with `approval_status='pending'`

2. **Admin Approves Listing**
   - Admin logs in to `/admin/dashboard`
   - Goes to `/admin/products` (Manage Products)
   - Finds pending listings
   - Clicks "Approve" button
   - Listing is updated with `approval_status='approved'`

3. **Listing Appears on Website**
   - Once approved, listing appears on `/browse` page
   - After first approval, listing appears on homepage (up to 12 most recent)
   - Users can filter by category: `/browse?category=Mobiles`
   - Users can click on listings to view full details

### Data Flow

```
User Posts Ad → Listing saved (approval_status='pending')
                    ↓
Admin Approves → Listing updated (approval_status='approved')
                    ↓
Home Page ← Shows 12 latest approved listings
Browse Page ← Shows all approved listings (with optional category filter)
```

## Testing the Feature

### Step 1: Create a Test User Account
```
1. Visit http://localhost:5000/register
2. Fill in details:
   - Role: Seller
   - Username: testuser
   - Email: test@example.com
   - Password: Password123
   - Phone: 1234567890
3. Click Register
```

### Step 2: Create an Admin Account
```
1. Go to database and insert admin user:
   INSERT INTO users (role, username, email, password, phone, created_at)
   VALUES ('admin', 'admin', 'admin@example.com', 'hashed_password', '0000000000', NOW());
```

### Step 3: Post a Listing
```
1. Login as seller user
2. Click "Sell" or visit http://localhost:5000/sell
3. Select a category (e.g., "Mobiles")
4. Select a subcategory
5. Fill in listing details:
   - Title: iPhone 13 Pro Max (example)
   - Price: 45000
   - Condition: Used
   - Description: Good condition phone with box
   - Photos: Upload at least 1 image
6. Click "Post ad"
7. You should see "Listing submitted for admin review" message
```

### Step 4: Approve the Listing (As Admin)
```
1. Login as admin user
2. Visit http://localhost:5000/admin/dashboard
3. Go to "Manage Products" (under Products section)
4. Find your pending listing
5. Click "Approve"
6. Listing status changes to approved
```

### Step 5: Verify on Homepage
```
1. Visit http://localhost:5000 (logout if needed)
2. Scroll down to "Featured Listings" section
3. You should see your approved listing
4. Click on listing to view details
```

### Step 6: Test Category Filtering
```
1. Visit http://localhost:5000/browse
2. In the "Category" filter, select a category
3. Page reloads and shows only listings in that category
4. URL changes to: http://localhost:5000/browse?category=YourCategory
5. All other filters (price, condition, location) work client-side
```

## Database Requirements

The feature requires these tables and columns:

### `listings` Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `category` - Category name (string)
- `subcategory` - Subcategory name (string)
- `title` - Listing title
- `description` - Full description
- `price` - Price in rupees
- `location` - Location/city
- `photos` - Comma-separated photo URLs
- `approval_status` - 'pending', 'approved', 'rejected', 'sold'
- `status` - 'active', 'archived'
- `created_at` - Timestamp

### `users` Table
- `id` - Primary key
- `username` - User name
- `email` - Email address
- `password` - Hashed password
- `role` - 'buyer', 'seller', 'admin', 'blocked'
- `phone` - Phone number
- `created_at` - Timestamp

## Features Summary

✓ Homepage displays up to 12 latest approved listings in Featured Listings section
✓ Browse page shows all approved listings with dynamic category list
✓ Category filtering works via URL parameters: `/browse?category=X`
✓ Search functionality filters by title, description, category
✓ Price, condition, and location filters work on browse page
✓ Responsive design works on mobile and desktop
✓ Empty states handled gracefully
✓ Listing cards show image, title, price, location, date
✓ Admin approval workflow controls what appears on site

## Future Enhancements

- [ ] Add pagination to browse/homepage listings
- [ ] Add favorite/bookmark listings feature
- [ ] Add reviews/ratings system
- [ ] Add messaging between buyers and sellers
- [ ] Add saved searches functionality
- [ ] Add email notifications for new listings in favorite categories
- [ ] Add advanced search filters (age, model, specs, etc.)
- [ ] Add listing expiration system
- [ ] Add analytics for sellers (views, clicks, conversions)
- [ ] Add promoted/featured listings system (paid boost)

## Troubleshooting

### Approved listings not showing on homepage
- **Issue**: Featured Listings section shows empty state
- **Solution**: Make sure you have at least one listing with `approval_status='approved'` in the database. Create a test listing and approve it through the admin panel.

### Category filter not showing all categories
- **Issue**: Category dropdown is empty or missing options
- **Solution**: The category options are dynamically fetched from the database. Make sure you have approved listings with different categories.

### Photos not displaying
- **Issue**: Listing cards show placeholder image instead of photo
- **Solution**: Check that:
  1. Photos were saved to `static/uploads/products/` directory
  2. Photo paths are stored correctly in the `photos` column (comma-separated)
  3. Web server has correct file permissions

### Database connection errors
- **Issue**: "Error loading featured listings" message
- **Solution**:
  1. Verify MySQL server is running
  2. Check database credentials in `get_db_connection()`
  3. Ensure `regear_db` database exists
  4. Verify all required tables exist

## Admin Panel Integration

The feature integrates with the existing admin panel at `/admin`:
- Admin can view pending, approved, and rejected listings
- Admin can approve listings using "Approve" button
- Admin can reject listings using "Reject" button
- Admin can delete listings using "Delete" button
- Admin logs are recorded for all actions

