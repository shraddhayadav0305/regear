# ReGear Category & Filter System - Complete Documentation

## 🎯 System Overview

This is a **production-ready, hierarchical category management system** with dynamic filters for the ReGear electronics marketplace. The system includes:

- **10 Main Categories** with full sub-category mapping
- **Dynamic Filter Management** - Create and assign filters per category
- **Admin Dashboard** - Full CRUD operations for categories, sub-categories, and filters
- **User-Facing Features** - Real-time filter search, sorting, and dynamic product discovery
- **Database-Driven** - Fully normalized MySQL schema with proper foreign keys

---

## 📊 Database Schema

### Tables Overview

```
categories (Main product categories)
├── id, name, slug, icon, color, display_order, is_active
├── created_at, updated_at
└── Foreign Keys: None (root level)

sub_categories (Sub-divisions within main categories)
├── id, category_id, name, slug, display_order, is_active
├── FOREIGN KEY: category_id → categories(id)
└── Composite Unique: (category_id, slug)

filter_types (Available filter types - Price, Condition, Brand, etc.)
├── id, name, slug, type (range|select|checkbox|multi_select)
├── is_active, created_at
└── Foreign Keys: None

filter_options (Predefined values for filters - e.g., "New", "Used", "64GB")
├── id, filter_type_id, option_value, option_label, display_order
├── FOREIGN KEY: filter_type_id → filter_types(id)
└── Composite Unique: (filter_type_id, option_value)

category_filters (Many-to-many mapping between categories and filters)
├── id, category_id, sub_category_id, filter_type_id
├── is_required, display_order, filter_config (JSON)
├── FOREIGN KEYS: category_id, sub_category_id, filter_type_id
└── Check: (category_id IS NOT NULL OR sub_category_id IS NOT NULL)

product_attributes (Actual filter values for each listing)
├── id, listing_id, filter_type_id, attribute_value
├── FOREIGN KEYS: listing_id → listings(id), filter_type_id → filter_types(id)
└── Composite Unique: (listing_id, filter_type_id)
```

---

## 🚀 Setup Instructions

### Step 1: Run Database Migration

```bash
python run_category_migration.py
```

This executes `CATEGORY_SYSTEM_SCHEMA.sql` and:
- Creates all required tables
- Inserts 10 main categories
- Inserts ~60 sub-categories with proper mappings
- Creates 15 filter types
- Assigns common filters to all categories
- Populates filter options (conditions, price ranges, etc.)

### Step 2: Update app.py

The main app.py has been updated to:
```python
from routes.categories import categories_bp
app.register_blueprint(categories_bp)  # Registers all category routes
```

### Step 3: Access Admin Dashboard

After login as admin:
```
http://localhost:5000/admin
```

New admin menu items:
- **Categories** → `/categories/admin/list` - Manage main categories
- **Sub-Categories** → `/categories/admin/subcategories` - Manage subcategories
- **Category Filters** → `/categories/admin/category/<id>/filters` - Assign filters

---

## 🗂️ 10 Main Categories (Included)

1. **Mobile Phones** - iPhone, Samsung, OnePlus, Xiaomi, Realme, etc.
2. **Laptops & Computers** - Gaming laptops, business laptops, desktops, tablets
3. **Computer Components** - GPU, CPU, RAM, Motherboards, PSU, Cooling
4. **Storage Devices** - HDD, SSD, NVMe, External storage, Memory cards
5. **Accessories** - Cables, adapters, chargers, power banks, docking stations
6. **Gaming Equipment** - Consoles, controllers, VR headsets, chairs
7. **Displays & Monitors** - Gaming monitors, 4K, curved, ultrawide, projectors
8. **Office Electronics** - Printers, scanners, multifunction devices
9. **Cameras & Photography** - DSLR, mirrorless, lenses, lighting, tripods
10. **Networking Hardware** - Routers, modems, switches, WiFi extenders

Each category has **5-6 sub-categories** (60 total) with relevant products.

---

## 🎛️ Filter Types (15 Available)

### Common Filters (Apply to All Categories)
- **Price Range** - Min/Max price selector
- **Condition** - New, Like New, Used, For Parts
- **Brand** - Manufacturer/brand name (multi-select)
- **Location** - City/state selector
- **Posted Date** - Last 24h, 7d, 30d, Any time

### Category-Specific Filters
- **Processor (CPU)** - For laptops/computers (Intel, AMD)
- **RAM** - 4GB, 8GB, 16GB, 32GB, 64GB options
- **Storage Type** - HDD, SSD, NVMe, Hybrid
- **Screen Size** - 13", 14", 15", 16", 17"
- **Mobile Brand** - iPhone, Samsung, OnePlus, Xiaomi, etc.
- **Storage Capacity** - 32GB, 64GB, 128GB, 256GB, 512GB, 1TB
- **Warranty Status** - With/Without warranty
- **Graphics Card** - GPU models
- **Resolution** - 1080p, 1440p, 4K, 5K
- **Refresh Rate** - 60Hz, 75Hz, 120Hz, 144Hz, 165Hz, 240Hz

---

## 📝 Admin Routes

### Categories Management
```
GET    /categories/admin/list                    → List all categories
GET    /categories/admin/create                  → Create category form
POST   /categories/admin/create                  → Save new category
GET    /categories/admin/edit/<id>               → Edit category form
POST   /categories/admin/edit/<id>               → Update category
POST   /categories/admin/delete/<id>             → Delete category (safe check)
```

### Sub-Categories Management
```
GET    /categories/admin/subcategories           → List all sub-categories
GET    /categories/admin/subcategory/create      → Create sub-category form
POST   /categories/admin/subcategory/create      → Save new sub-category
GET    /categories/admin/subcategory/edit/<id>  → Edit sub-category form
POST   /categories/admin/subcategory/edit/<id>  → Update sub-category
POST   /categories/admin/subcategory/delete/<id>→ Delete sub-category
```

### Filter Management
```
GET    /categories/admin/category/<id>/filters          → Manage filters for category
POST   /categories/admin/category-filter/assign         → Assign filter to category
POST   /categories/admin/category-filter/remove/<id>    → Remove filter from category
```

---

## 🔌 Public API Routes

### Get Categories & Sub-Categories
```
GET    /categories/api/all                       → All categories with subcategories
GET    /categories/api/category/<slug>           → Single category with filters
GET    /categories/api/subcategory/<id>/filters  → Filters for subcategory
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "mobile-phones": {
      "id": 1,
      "name": "Mobile Phones",
      "icon": "📱",
      "subcategories": [
        {"id": 1, "name": "Apple iPhone", "slug": "apple-iphone"},
        {"id": 2, "name": "Samsung Galaxy", "slug": "samsung-galaxy"}
      ]
    }
  }
}
```

---

## 🛠️ Implementation Guide

### 1. Adding a New Category (Admin)

1. Navigate to Admin → Categories → "+ New Category"
2. Fill in:
   - **Name**: User-friendly name (e.g., "Smart Home Devices")
   - **Slug**: URL-safe identifier (e.g., "smart-home-devices")
   - **Icon**: Emoji (🏠) or Font Awesome (fas fa-home)
   - **Color**: Hex color code (#0066cc)
   - **Display Order**: Determines position in listing
   - **Description**: Brief category description
3. Click "Create Category"

### 2. Adding Sub-Categories

1. Go to Admin → Sub-Categories → "+ New Sub-Category"
2. Select parent category
3. Fill in name, slug, description, display order
4. Repeat for all sub-divisions

### 3. Assigning Filters to Category

1. Go to Admin → Categories
2. Click **Filter icon** (🎛️) on any category
3. Available filters shown on right
4. Click "+ Assign Filter" and select from dropdown
5. Set display order and whether required
6. Click "Assign Filter"

---

## 📋 Using in Post Ad Form

When a user creates a listing:

1. **Select Main Category** → Fetches from `/categories/api/all`
2. **Select Sub-Category** → Dynamically updated in dropdown
3. **Fill Filters** → Fetch from `/categories/api/subcategory/<id>/filters`
4. **Submit Listing** → Store in `product_attributes` table

Example flow:
```javascript
// User selects "Mobile Phones"
fetch('/categories/api/category/mobile-phones')
  .then(r => r.json())
  .then(data => {
    // Populate sub-category dropdown with data.subcategories
    // Fetch filters for selected subcategory
    fetch('/categories/api/subcategory/1/filters')
      .then(r => r.json())
      .then(filters => {
        // Display price range, condition, brand filters
      });
  });
```

---

## 🔍 Search & Filter Features

### Frontend Filtering (browse_listings.html)
- **Real-time JavaScript filtering** - No server calls needed
- **Price Range** - Min/Max inputs
- **Multi-select Conditions** - Checkbox filters
- **Location Search** - Text input with live matching
- **Dynamic Sorting** - Newest, oldest, price low-to-high, etc.
- **Mobile-Responsive** - Collapsible filter sidebar on mobile

### Backend Search (Future Enhancement)
Ready for server-side search route:
```python
@app.route('/api/search')
def search():
    category_id = request.args.get('category_id')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    condition = request.args.get('condition')
    # Query listings with product_attributes JOIN
    # Return paginated results
```

---

## 🔐 Safety Features

### Delete Protection
- **Cannot delete categories with listings** - Shows error count
- **Cannot delete sub-categories with listings** - Same protection
- **Prevent duplicate slugs** - Enforced in database and backend

### Data Validation
- **Required fields check** - Name, slug, category_id
- **Slug format validation** - Lowercase, hyphens only
- **Unique constraint checks** - Prevent duplicates

### Admin-Only Routes
- All `/categories/admin/*` routes protected with `@admin_required` decorator
- Public API routes (`/categories/api/*`) accessible to all

---

## 📈 Scalability

### Adding New Filter Types

1. Insert into `filter_types`:
```sql
INSERT INTO filter_types (name, slug, type, is_active)
VALUES ('RAM', 'ram', 'multi_select', 1);
```

2. Add filter options:
```sql
INSERT INTO filter_options (filter_type_id, option_value, option_label)
VALUES (7, '8gb', '8 GB');
```

3. Assign to category:
```sql
INSERT INTO category_filters (category_id, filter_type_id, is_required, display_order)
VALUES (2, 7, 1, 6);  -- Required RAM filter for category 2 (Laptops)
```

### Adding New Categories

Use admin UI or SQL:
```sql
INSERT INTO categories (name, slug, icon, color, display_order)
VALUES ('Wearables', 'wearables', '⌚', '#FF5722', 11);

-- Then add sub-categories and filters
```

---

## 🧪 Testing

### Manual Testing

1. **Category CRUD**:
   - Create category → Verify in list
   - Edit category → Verify changes saved
   - Delete category with no listings → Success
   - Try delete with listings → Error message

2. **Sub-Category CRUD**:
   - Create sub-categories under different parents
   - Verify grouping in admin list
   - Test delete protection

3. **Filter Assignment**:
   - Assign multiple filters to category
   - Verify display order
   - Mark some as required
   - Remove filters

4. **API Endpoints**:
   - Test `/categories/api/all` → All categories returned
   - Test `/categories/api/category/mobile-phones` → Correct category
   - Test `/categories/api/subcategory/1/filters` → Correct filters

5. **Browse/Search**:
   - Filter by price range
   - Filter by condition
   - Search by location
   - Sort by different options
   - Verify counts update

---

## 📦 File Structure

```
regear/
├── app.py                          (Updated with blueprint import)
├── routes/
│   ├── categories.py              ✨ NEW - All category routes
│   └── admin.py                    (Existing admin routes)
├── templates/
│   ├── admin/
│   │   ├── admin_categories.html           ✨ NEW
│   │   ├── admin_category_form.html        ✨ NEW
│   │   ├── admin_subcategories.html        ✨ NEW
│   │   ├── admin_subcategory_form.html     ✨ NEW
│   │   └── admin_category_filters.html     ✨ NEW
│   ├── browse_listings.html               ✨ UPDATED - With filters
│   └── ...
├── CATEGORY_SYSTEM_SCHEMA.sql             ✨ NEW
└── run_category_migration.py              ✨ NEW
```

---

## 🚨 Troubleshooting

### "Database migration failed"
- Ensure MySQL is running
- Check credentials in `run_category_migration.py`
- Try running queries manually in MySQL Workbench

### "Category not appearing in dropdown"
- Check `is_active = 1` in database
- Verify `display_order` is set
- Clear browser cache

### "Filters not showing in post form"
- Run migration script
- Check `category_filters` table has entries
- Verify filters are assigned to category

### "Admin routes returning 403"
- Login as admin account (role='admin')
- Check session is set correctly

---

## 📝 API Integration Example

```javascript
// Get all categories
async function loadCategories() {
    const response = await fetch('/categories/api/all');
    const data = await response.json();
    return data.data;
}

// Get specific category with filters
async function loadCategoryFilters(slug) {
    const response = await fetch(`/categories/api/category/${slug}`);
    const data = await response.json();
    return data.data;
}

// Get filters for subcategory
async function loadSubcategoryFilters(subcatId) {
    const response = await fetch(`/categories/api/subcategory/${subcatId}/filters`);
    const data = await response.json();
    return data.data;
}
```

---

## 🎓 Next Steps

1. ✅ Run database migration
2. ✅ Restart Flask server
3. ✅ Login as admin
4. ✅ Go to Admin → Categories to see all categories
5. ✅ Test creating/editing categories and sub-categories
6. ✅ Assign filters to categories
7. ✅ Update post ad form to use new category system
8. ✅ Test creating listings with filters
9. ✅ Test search and filtering on browse page

---

## 📞 Support & Customization

**For custom categories/filters:**
- Edit initial data in `CATEGORY_SYSTEM_SCHEMA.sql`
- Add new filter types via admin UI
- Assign filters per category as needed

**For API customization:**
- Edit routes in `routes/categories.py`
- Modify response format in API endpoints
- Add server-side search if needed

---

## 📄 License & Credits

Part of **ReGear** Electronics Marketplace Platform
Complete hierarchical category system suitable for any OLX-style marketplace

---

Last Updated: 2024
Version: 1.0 - Production Ready
