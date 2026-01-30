# 🚀 ReGear Complete Setup & Testing Guide

## Prerequisites

### Install Required Packages
```bash
pip install flask mysql-connector-python
```

### Database Setup

#### 1. Create Database
```sql
CREATE DATABASE regear_db;
USE regear_db;
```

#### 2. Create Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    role ENUM('buyer', 'seller') DEFAULT 'buyer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. Verify Table Creation
```sql
DESC users;
```

Expected Output:
```
Field      | Type                    | Null | Key | Default
-----------|-------------------------|------|-----|--------
id         | int                     | NO   | PRI | NULL
username   | varchar(100)            | NO   | UNI | NULL
email      | varchar(100)            | NO   | UNI | NULL
phone      | varchar(20)             | YES  |     | NULL
password   | varchar(255)            | NO   |     | NULL
role       | enum('buyer','seller')  | NO   |     | buyer
created_at | datetime                | YES  |     | CURRENT_TIMESTAMP
```

---

## Running the Application

### 1. Start Flask Server
```bash
cd c:\Users\sysadmin\OneDrive\Desktop\regear
python app.py
```

### Expected Console Output:
```
✅ Database connected successfully!
🚀 Starting ReGear Server...
📍 Server running at: http://localhost:5000
📝 Register: http://localhost:5000/register
🔐 Login: http://localhost:5000/login
```

### 2. Access the Application
```
http://localhost:5000
```

---

## Complete End-to-End Testing

### TEST 1: Health Check ✅
**Purpose:** Verify server and database are running

```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "ReGear server is running",
  "database": "connected"
}
```

---

### TEST 2: Registration Flow ✅

#### Step 1: Navigate to Registration
- Open: http://localhost:5000/register
- ✅ See: Professional registration form with gradient background
- ✅ See: Role selector (Buy Items / Sell Items)
- ✅ See: Form fields for Full Name, Email, Phone, Password

#### Step 2: Select Role
- Click on **"Buy Items"** or **"Sell Items"**
- ✅ See: Selected role highlights in blue
- ✅ Verify: Role is saved in hidden field

#### Step 3: Fill Registration Form
```
Full Name: John Smith
Email: john.smith@example.com
Phone: 555-123-4567
Password: MySecure123!
Confirm Password: MySecure123!
Terms: ✓ (check box)
```

#### Step 4: Submit Registration
- Click: **"Create Account"** button
- ✅ See: Loading spinner during submission
- ✅ See: Success message - "✅ Account created successfully! Please login now."
- ✅ Auto-redirect: To /login page

#### Step 5: Verify Database Entry
```bash
# In MySQL:
SELECT * FROM users WHERE email = 'john.smith@example.com';
```

**Expected Output:**
```
id | username   | email                | phone        | password | role  | created_at
1  | John Smith | john.smith@exam...  | 555-123-...  | sa$8f... | buyer | 2024-01-...
```

Note: `password` field shows `salt$hash` format (secure)

---

### TEST 3: Registration Error Handling ✅

#### Test 3a: Duplicate Email
```
1. Fill form with same email from TEST 2
2. Submit
Expected: ❌ Email already registered! Please login.
Behavior: Form stays on /register
```

#### Test 3b: Duplicate Username
```
1. Fill form with same full name from TEST 2
2. Submit
Expected: ❌ Username already taken! Try another.
Behavior: Form stays on /register
```

#### Test 3c: Short Username
```
Full Name: Jo
Expected: ❌ Username must be at least 3 characters!
```

#### Test 3d: Invalid Email
```
Email: notanemail
Expected: ❌ Please enter a valid email!
```

#### Test 3e: Short Password
```
Password: 12345
Expected: ❌ Password must be at least 6 characters!
```

#### Test 3f: Password Mismatch
```
Password: MySecure123!
Confirm: MySecure456!
Expected: Frontend validation: "❌ Passwords do not match"
```

#### Test 3g: Terms Not Checked
```
Skip: Check Terms & Conditions box
Expected: ❌ Please agree to Terms & Conditions
```

---

### TEST 4: Login Flow ✅

#### Step 1: Navigate to Login
- URL: http://localhost:5000/login
- ✅ See: Professional login form with gradient background
- ✅ See: Email and password fields

#### Step 2: Enter Valid Credentials
```
Email: john.smith@example.com
Password: MySecure123!
```

#### Step 3: Submit Login
- Click: **"Sign In"** button
- ✅ See: Loading spinner
- ✅ See: Success message - "✅ Welcome back, John Smith!"
- ✅ Auto-redirect: To /dashboard

#### Step 4: Verify Session Created
- Browser console → Application → Cookies
- ✅ See: `session` cookie with value

---

### TEST 5: Login Error Handling ✅

#### Test 5a: Wrong Password
```
Email: john.smith@example.com
Password: WrongPassword123!
Expected: ❌ Invalid email or password!
Behavior: Form stays on /login
```

#### Test 5b: Non-existent Email
```
Email: nonexistent@example.com
Password: AnyPassword123!
Expected: ❌ Invalid email or password!
Behavior: Form stays on /login
```

#### Test 5c: Missing Email
```
Email: (empty)
Password: MySecure123!
Expected: ❌ Please fill in all fields!
```

#### Test 5d: Missing Password
```
Email: john.smith@example.com
Password: (empty)
Expected: ❌ Please fill in all fields!
```

---

### TEST 6: Dashboard Access ✅

#### Step 1: After Successful Login
- ✅ See: Personalized greeting - "Welcome, John Smith! 👋"
- ✅ See: User role badge - "Buyer Account" or "Seller Account"
- ✅ See: User avatar with first letter "J" in purple circle
- ✅ See: Sticky navbar at top with logout button

#### Step 2: Role-Specific Content

**If Buyer Account:**
- ✅ Quick Actions:
  1. Browse Items - Browse thousands of items
  2. Saved Items - View your liked items
  3. My Orders - Track your purchases

**If Seller Account:**
- ✅ Quick Actions:
  1. Post New Item - List a new product
  2. My Listings - Manage your products
  3. Sales Analytics - View sales data

#### Step 3: Dashboard Components
- ✅ See: Statistics cards (4 total)
  - Total Orders
  - Total Revenue
  - Active Listings
  - Customer Ratings
- ✅ See: Smooth animations on hover
- ✅ See: Fully responsive layout (test on mobile/tablet)

---

### TEST 7: Logout Flow ✅

#### Step 1: Click Logout
- Location: Navbar at top right
- Click: **Logout** button
- ✅ See: Confirmation dialog - "Are you sure you want to logout?"

#### Step 2: Confirm Logout
- Click: **"Yes, Logout"** button
- ✅ See: Success message - "✅ Logged out successfully!"
- ✅ Auto-redirect: To /login page

#### Step 3: Verify Session Cleared
- Try to access: http://localhost:5000/dashboard
- ✅ Expected: Redirect to /login
- ✅ Message: "Please login first!"

---

### TEST 8: Session Persistence ✅

#### Step 1: Login
- Email: john.smith@example.com
- Password: MySecure123!

#### Step 2: Navigate Between Pages
- From dashboard, click quick action link
- ✅ Session should persist (no re-login required)

#### Step 3: Browser Refresh
- Press: F5 on dashboard page
- ✅ Expected: Dashboard still loads (session intact)

#### Step 4: Manual Navigation
- Enter URL: http://localhost:5000/dashboard
- ✅ Expected: Dashboard loads (session valid)

---

### TEST 9: Create Multiple Users ✅

**Test Different Roles:**

#### User 1: Buyer
```
Name: Alice Johnson
Email: alice@example.com
Role: Buy Items
Password: Buyer123!
```

#### User 2: Seller
```
Name: Bob Wilson
Email: bob@example.com
Role: Sell Items
Password: Seller456!
```

#### User 3: Another Buyer
```
Name: Charlie Brown
Email: charlie@example.com
Role: Buy Items
Password: Charlie789!
```

#### Verify Login As Each
- ✅ Each user sees correct role on dashboard
- ✅ Each user sees role-specific quick actions
- ✅ Each user's name shown in personalized greeting

---

### TEST 10: Edge Cases ✅

#### Test 10a: SQL Injection Prevention
```
Email: ' OR '1'='1
Expected: ❌ Invalid email or password!
Behavior: No database error, injection prevented by parameterized queries
```

#### Test 10b: Special Characters in Name
```
Full Name: José García-Smith
Expected: ✅ Works fine, special characters handled
```

#### Test 10c: Very Long Email
```
Email: verylongemailaddress@subdomain.example.co.uk
Expected: ✅ Works fine, up to 100 characters allowed
```

#### Test 10d: Case Sensitivity
```
Register: Email = John@Example.com
Login: Email = john@example.com
Expected: MySQL may be case-insensitive on some systems
Note: Consider making email lowercase in code: email.lower()
```

---

## Performance Testing

### Load the Dashboard Multiple Times
```bash
# In PowerShell:
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
1..10 | % { 
    Invoke-WebRequest -Uri "http://localhost:5000/dashboard" -WebSession $session
}
```

**Expected:** All requests succeed, dashboard loads consistently

---

## Browser DevTools Testing

### F12 → Network Tab
1. Register new user
2. Observe network requests:
   - ✅ POST /register
   - ✅ 302 Redirect to /login
   - ✅ GET /login

3. Login
4. Observe:
   - ✅ POST /login
   - ✅ 302 Redirect to /dashboard
   - ✅ GET /dashboard
   - ✅ Set-Cookie (session)

### F12 → Application Tab
1. After login, check Cookies
   - ✅ See: `session` cookie
   - ✅ HttpOnly: Yes (security)
   - ✅ Secure: (depends on HTTPS)

---

## Database Verification Commands

```sql
-- Check all users
SELECT id, username, email, role, created_at FROM users;

-- Count by role
SELECT role, COUNT(*) as count FROM users GROUP BY role;

-- Check specific user
SELECT * FROM users WHERE email = 'john.smith@example.com';

-- Clear all users (for fresh testing)
DELETE FROM users;
```

---

## Common Issues & Solutions

### Issue 1: Database Connection Failed
```
Error: ❌ Database connection failed: Access denied for user 'root'
Solution:
- Verify MySQL is running
- Check username: root
- Check password: Shra@0303
- Verify database exists: regear_db
```

### Issue 2: Template Not Found
```
Error: TemplateNotFound: register.html
Solution:
- Ensure templetes/ folder exists (note: typo "templetes" not "templates")
- Verify file names match: register.html, login.html, dashboard.html
```

### Issue 3: Form Not Submitting
```
Error: Form stays on same page, no error message
Solution:
- Check browser console (F12) for JavaScript errors
- Verify form action="/register" matches route
- Verify input names match backend expectations
```

### Issue 4: Login Always Fails
```
Error: ❌ Invalid email or password! (even with correct credentials)
Solution:
- Check password was hashed during registration
- Verify password field in database stores hash
- Ensure password hashing function is consistent
```

### Issue 5: Session Not Persisting
```
Error: Redirected to login after page refresh
Solution:
- Verify app.secret_key is set
- Check SESSION_PERMANENT = False is correct
- Verify session variables are set in /login route
```

---

## Security Checklist

- [x] Passwords hashed with SHA-256 + salt
- [x] SQL injection prevented (parameterized queries)
- [x] Session secret key set and not hardcoded in production
- [x] login_required decorator protects routes
- [x] Email and username uniqueness enforced
- [x] Input validation on both frontend and backend
- [x] Error messages don't leak sensitive info
- [x] Logout clears entire session
- [x] HTTPS recommended for production

---

## Next Steps After Testing

1. ✅ Create additional pages:
   - Browse/Search items page
   - Post new item page
   - View item details page
   - User profile page

2. ✅ Add features:
   - Email verification
   - Password reset
   - User profile update
   - Item listing with images

3. ✅ Database optimization:
   - Add indexing on frequently searched columns
   - Consider caching for performance

4. ✅ Production deployment:
   - Change debug=False
   - Use environment variables for secrets
   - Deploy to Heroku, AWS, or similar

---

## Troubleshooting Checklist

Before reporting issues, verify:

- [ ] MySQL is running: `mysql -u root -p`
- [ ] Database exists: `SHOW DATABASES;`
- [ ] Users table exists: `DESC users;`
- [ ] Flask is running without errors
- [ ] All files in correct locations
- [ ] Form field names are exact (case-sensitive)
- [ ] Browser console has no JavaScript errors
- [ ] Cookies are enabled in browser
- [ ] Ports 5000 is not in use by another app

---

**Status:** ✅ Ready for testing
**Created:** Current date
**Application:** ReGear - Buy/Sell Platform
**Components:** Flask Backend, MySQL Database, Bootstrap Frontend
