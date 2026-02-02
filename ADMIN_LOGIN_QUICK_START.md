# Admin Login - Quick Start Guide

## Login to Admin Dashboard (30 seconds)

### Step 1: Start Server
```bash
python app.py
```
Server runs at: http://localhost:5000

### Step 2: Go to Login Page
Visit: http://localhost:5000/login

### Step 3: Enter Admin Credentials
- **Email**: admin@regear.com
- **Password**: admin123

### Step 4: Click Login
✅ You'll be automatically redirected to the admin dashboard!

---

## Admin Dashboard Features

Once logged in at `/admin/dashboard`, you have access to:

### 📊 Dashboard
- Total users count
- Active users today
- Blocked users
- Total listings
- Pending listings
- Recent activity
- Top sellers

### 👥 User Management (`/admin/users`)
- View all users
- Search by email/username
- Block/unblock accounts
- View user details
- User activity history

### 📦 Product Management (`/admin/products`)
- View all listings
- Approve listings
- Reject listings
- View product details
- Track listing status

### 📋 Complaints (`/admin/complaints`)
- View user complaints
- Resolve complaints
- Dismiss complaints
- Filter by status
- Add notes/actions

### 📈 Activity (`/admin/activity`)
- View all admin actions
- Audit trail
- Action history
- Timestamps

---

## How It Works (Behind the Scenes)

### Login Flow
```
1. You submit email + password at /login
2. Flask app verifies password against database
3. App checks user role in database
4. If role == 'admin', redirects to /admin/dashboard
5. Admin blueprint receives request
6. @admin_required decorator validates you're admin
7. Dashboard function fetches statistics
8. Dashboard template displays with your data
```

### Security
- ✅ Only users with role='admin' can access admin pages
- ✅ Non-admin users get redirected to home
- ✅ Session variable checks on every admin route
- ✅ Passwords are SHA-256 hashed

---

## Test Login Flow Programmatically

```bash
python test_admin_login.py
```

Expected output:
```
============================================================
Testing Admin Login Flow
============================================================

1️⃣ Accessing login page...
   Status: 200

2️⃣ Submitting login form...
   Status: 302
   Redirect location: /admin/dashboard

3️⃣ Following redirect to: http://localhost:5000/admin/dashboard
   Status: 200
   ✅ Successfully redirected to admin dashboard!

============================================================
✅ Admin login connection SUCCESSFUL!
============================================================
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't login with admin credentials | Check if admin user exists: `python check_users.py` |
| Login works but redirects to home | Admin's role might not be 'admin' in database |
| /admin/dashboard shows error | Check server logs, might be database connection issue |
| Can't see admin menu | Make sure you're logged in AND role is 'admin' |

---

## Database Check

To verify admin user exists:
```bash
python check_users.py
```

Should show:
```
ID: 3, Username: admin, Email: admin@regear.com, Role: admin
```

---

## Next Steps

Once admin login is working:

1. **Create more admin users** (if needed)
   - Use /register with role='admin' (requires backend change)
   - Or add directly to database

2. **Customize admin dashboard**
   - Edit `templates/admin/admin_dashboard.html`
   - Add new widgets
   - Change styling

3. **Extend admin features**
   - Add new routes in `routes/admin.py`
   - Create new templates in `templates/admin/`
   - Add database queries

---

## Key Files

| File | Purpose |
|------|---------|
| app.py | Login logic + redirect to admin |
| routes/admin.py | All admin routes + decorators |
| templates/admin/admin_dashboard.html | Dashboard view |
| templates/admin/admin_layout.html | Admin navigation + base template |

---

**Everything is connected and working!** ✅
The admin login seamlessly redirects to the admin dashboard.
