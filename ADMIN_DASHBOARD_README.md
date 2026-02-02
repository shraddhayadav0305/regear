# ReGear Admin Dashboard - Complete Implementation Guide

## Overview

The ReGear Admin Dashboard is a comprehensive, production-ready admin control panel for managing the second-hand electronics marketplace. It provides complete functionality for user management, product approval, complaints handling, and activity monitoring.

## Features

### 1. **Dashboard Overview**
- **Real-time Statistics**: Total users, active users, blocked users, listings, pending approvals
- **Charts & Analytics**: Product growth, user growth trends (last 7 days)
- **Recent Activity**: Live feed of recent user and admin actions
- **Top Sellers**: Performance metrics for active sellers
- **Quick Actions**: One-click access to all admin functions

### 2. **User Management**
- View all registered users with detailed profiles
- Search users by email or username
- Filter by role (buyers, sellers, blocked)
- Block/unblock users with custom reasons
- View user's listings and complaint history
- Track warning count and suspension status
- Automatic suspension after 3 warnings

### 3. **Product Approval System**
- Approve/reject listings before publishing
- All products start in 'pending' status
- Only approved products visible to buyers
- Bulk management of pending approvals
- Search and filter by status, category
- Add admin notes during approval/rejection

### 4. **Complaints & Reports**
- Manage user reports (scam, fraud, fake listings, inappropriate)
- Categorized complaint handling
- Take actions: dismiss, warn, or block users
- Track complaint resolution
- View complaint history per user

### 5. **Activity Monitoring**
- Audit trail of all admin actions
- Track block/unblock, approve/reject, delete operations
- View who performed what action and when
- Detailed logging for compliance

### 6. **Modern UI & Responsive Design**
- Professional dark sidebar navigation
- Bootstrap 5 responsive grid
- Modal dialogs for actions
- Real-time charts with Chart.js
- Mobile-friendly tables
- Color-coded badges for status

## File Structure

```
regear/
├── routes/
│   └── admin.py                    # All admin routes and logic
├── templates/admin/
│   ├── admin_layout.html          # Base layout with sidebar
│   ├── admin_dashboard.html       # Dashboard overview
│   ├── admin_users.html           # User management
│   ├── admin_products.html        # Product approval
│   ├── admin_complaints.html      # Complaints handling
│   ├── admin_activity.html        # Activity logs
│   └── admin_user_detail.html     # User details page
├── static/admin/
│   ├── css/
│   │   └── admin_style.css       # Admin styling
│   └── js/
│       └── admin_script.js       # Admin functionality
├── ADMIN_SCHEMA.sql              # Database migration script
└── app.py                        # Main app (updated with admin blueprint)
```

## Database Schema

### New Tables Created

1. **admin_logs**
   - Tracks all admin actions (block, approve, reject, delete)
   - Fields: id, admin_id, action, description, table_affected, record_id, created_at

2. **complaints**
   - Stores user reports about other users/listings
   - Fields: id, reporter_id, reported_user_id, listing_id, complaint_type, reason, status, admin_action, admin_id, created_at, resolved_at

3. **activity_logs**
   - Tracks user activities on the platform
   - Fields: id, user_id, activity_type, description, ip_address, user_agent, created_at

4. **admin_announcements**
   - For admin notifications and announcements
   - Fields: id, admin_id, title, message, status, created_at

### Modified Tables

1. **listings**
   - Added: approval_status (pending/approved/rejected/sold), admin_notes, approved_by, approved_at
   - All new listings default to approval_status='pending'

2. **users**
   - Added: warning_count, last_warning_at, suspension_reason
   - Track user violations and automatic suspension

## Setup Instructions

### 1. **Database Migration**

Run the SQL migration script to create new tables and columns:

```bash
mysql -u root -p Shra@0303 regear_db < ADMIN_SCHEMA.sql
```

Or in MySQL client:
```sql
SOURCE /path/to/ADMIN_SCHEMA.sql;
```

### 2. **Create Admin User**

```bash
# In MySQL client
INSERT INTO users (role, username, email, password, phone, created_at) 
VALUES ('admin', 'admin', 'admin@regear.com', SHA2(CONCAT('salt', 'password'), 256), '1234567890', NOW());
```

Or register as admin in the application (requires manual role update):
```sql
UPDATE users SET role='admin' WHERE id=1;
```

### 3. **Access Admin Panel**

1. Login with admin credentials
2. Navigate to `http://localhost:5000/admin/dashboard`
3. Or click "Admin Panel" link if available in menu

## Routes

### Dashboard Routes
- `GET /admin/dashboard` - Main admin dashboard with stats
- `GET /admin/users` - User management page
- `GET /admin/user/<user_id>` - View user details
- `GET /admin/products` - Product management page
- `GET /admin/complaints` - Complaints management
- `GET /admin/activity` - Activity logs

### User Management Routes
- `POST /admin/user/<user_id>/block` - Block a user
- `POST /admin/user/<user_id>/unblock` - Unblock a user

### Product Management Routes
- `POST /admin/product/<product_id>/approve` - Approve a listing
- `POST /admin/product/<product_id>/reject` - Reject a listing
- `POST /admin/product/<product_id>/delete` - Delete a listing

### Complaint Routes
- `POST /admin/complaint/<complaint_id>/resolve` - Resolve complaint with action (warn/block)

### API Routes
- `GET /admin/api/chart-data` - Get chart data for dashboard

## Security Features

### Authentication & Authorization
- `@admin_required` decorator protects all admin routes
- Session-based authentication checking role='admin'
- Automatic redirect to login for non-admin users

### Password Security
- SHA-256 hashing with salt
- All stored passwords hashed in database
- Legacy password verification support

### Audit Logging
- All admin actions logged to admin_logs table
- Includes admin ID, action, affected table, timestamp
- Enables compliance tracking

### Input Validation
- All form inputs sanitized
- Parameterized SQL queries prevent injection
- File uploads handled with secure_filename

## Usage Examples

### Approve a Product

1. Go to `/admin/products`
2. Filter by "Pending Approval"
3. Click the green checkmark icon
4. Enter optional admin notes
5. Click "Approve"
6. Product automatically becomes visible to buyers

### Block a User

1. Go to `/admin/users`
2. Click the eye icon to view user details
3. Click "Block User"
4. Enter reason for blocking
5. Click "Block User"
6. User's role changes to 'blocked'
7. User cannot login or post

### Resolve a Complaint

1. Go to `/admin/complaints`
2. Click eye icon on pending complaint
3. Choose action: dismiss, warn, or block
4. Enter admin notes
5. Click "Submit Action"
6. If warn: warning_count incremented (auto-block at 3)
7. If block: user role set to 'blocked'

### View Analytics

1. Go to `/admin/dashboard`
2. Charts show product and user growth (last 7 days)
3. View recent activity feed
4. See top sellers by listing count
5. Monitor pending approvals and blocked users

## API Endpoints

### Chart Data API
```
GET /admin/api/chart-data
Response:
{
  "products": [
    {"date": "2024-01-01", "count": 5},
    ...
  ],
  "users": [
    {"date": "2024-01-01", "count": 3},
    ...
  ],
  "categories": [
    {"category": "Mobiles", "count": 15},
    ...
  ]
}
```

## Customization

### Add New Admin User
```python
# In app.py or direct DB
cursor.execute("""
    INSERT INTO users (role, username, email, password, phone, created_at)
    VALUES ('admin', 'newadmin', 'email@example.com', hash_password('pass123'), '9876543210', NOW())
""")
```

### Modify Dashboard Statistics
Edit `/routes/admin.py` in the `dashboard()` function to add/remove statistics cards.

### Change Approval Workflow
- Edit product status values in `/routes/admin.py`
- Update status options in templates
- Modify visibility logic in main app.py

### Add New Complaint Types
Update complaint_type enum in database:
```sql
ALTER TABLE complaints MODIFY complaint_type ENUM('scam', 'fraud', 'fake_listing', 'inappropriate', 'duplicate', 'other');
```

Then update templates to show new types.

## Performance Optimization

### Pagination
- All tables paginated with 10 items per page
- Can modify `items_per_page` in `/routes/admin.py`

### Database Indexes
- Indexes on admin_logs.admin_id, complaints.status, activity_logs.user_id
- Enables fast filtering and searching

### Caching
- Consider adding Redis for chart data caching
- Cache user roles/permissions

## Troubleshooting

### Admin Dashboard Not Accessible
- Verify user role is 'admin': `SELECT role FROM users WHERE id=YOUR_ID;`
- Check session contains user_id: `session.get('user_id')`
- Ensure blueprint registered in app.py

### Database Schema Missing
- Run ADMIN_SCHEMA.sql: `mysql -u root -p Shra@0303 regear_db < ADMIN_SCHEMA.sql`
- Verify tables exist: `SHOW TABLES;`

### Charts Not Displaying
- Check browser console for JavaScript errors
- Verify Chart.js loaded: `<script src="...chart.min.js">`
- Check `/admin/api/chart-data` returns valid JSON

### Admin Actions Not Logging
- Verify admin_logs table exists
- Check log_admin_action function called in routes
- Inspect admin_logs table: `SELECT * FROM admin_logs LIMIT 10;`

## Features Completed

✅ Dashboard overview with real-time statistics
✅ User management with block/unblock functionality
✅ Product approval system (pending → approved → published)
✅ Complaints & reports handling with actions
✅ Activity logging & audit trail
✅ Advanced charts & analytics
✅ Search and filtering across all modules
✅ Pagination for all list pages
✅ Modal dialogs for confirmations
✅ Responsive mobile-friendly design
✅ Professional modern UI with sidebar
✅ Complete authentication & authorization
✅ Database schema with proper relationships
✅ Security features (parameterized queries, hashing)

## Future Enhancements

- Email notifications for admin actions
- Bulk operations (block multiple users, approve batch)
- Advanced filtering (date range, price range)
- Export data to CSV/PDF
- User activity timeline
- Seller rating/reviews management
- Category management panel
- System settings/configuration
- Two-factor authentication for admin
- Real-time WebSocket notifications
- Mobile app for admin
- API integration for third-party tools

## Support & Documentation

For issues or questions:
1. Check browser console (F12) for JavaScript errors
2. Check Flask logs for backend errors
3. Verify database migrations executed
4. Review `ADMIN_SCHEMA.sql` for expected tables
5. Check route implementations in `/routes/admin.py`
6. Test with MySQL: `mysql -u root -p`

---

**ReGear Admin Dashboard v1.0** - Production Ready
