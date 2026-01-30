# ✅ ReGear System - Complete Connectivity Overview

## 🎯 SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    REGEAR PLATFORM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  FRONTEND    │  │   BACKEND    │  │   DATABASE   │     │
│  │              │  │              │  │              │     │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤     │
│  │register.html │  │ Flask App    │  │  MySQL DB    │     │
│  │login.html    │  │ (app.py)     │  │  (regear_db) │     │
│  │dashboard.html│  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│        │                  │                  │             │
│        └──────────────────┴──────────────────┘             │
│              HTTP Requests/Responses                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 COMPLETE FLOW DIAGRAM

```
START
  │
  ├─→ http://localhost:5000
  │   (Home Page)
  │   │
  │   ├─→ /register (NEW USER)
  │   │   │
  │   │   ├─ Display: register.html ✅
  │   │   │   └─ Role Selector: Buyer/Seller
  │   │   │   └─ Form Fields: username, email, phone, password, role (hidden)
  │   │   │
  │   │   ├─ USER FILLS FORM
  │   │   │   └─ JavaScript validation (frontend)
  │   │   │   └─ Show password strength indicator
  │   │   │   └─ Check passwords match
  │   │   │
  │   │   └─ POST /register ✅
  │   │       │
  │   │       ├─ Flask Backend Processing:
  │   │       │  ├─ Extract: role, username, email, phone, password
  │   │       │  ├─ Validate: username length, email format, password length
  │   │       │  ├─ Check: email not duplicate
  │   │       │  ├─ Check: username not duplicate
  │   │       │  ├─ Hash: password with SHA-256 + salt
  │   │       │  └─ INSERT: user to MySQL database
  │   │       │
  │   │       └─ Response:
  │   │           ├─ Success: "✅ Account created successfully!"
  │   │           ├─ Flash message displayed
  │   │           └─ Redirect: to /login ✅
  │   │
  │   └─→ /login (EXISTING OR NEW USER)
  │       │
  │       ├─ Display: login.html ✅
  │       │   └─ Form Fields: email, password
  │       │
  │       ├─ USER ENTERS CREDENTIALS
  │       │   └─ JavaScript validation (frontend)
  │       │
  │       └─ POST /login ✅
  │           │
  │           ├─ Flask Backend Processing:
  │           │  ├─ Extract: email, password
  │           │  ├─ Query: SELECT user WHERE email = %s
  │           │  ├─ Verify: password matches stored hash
  │           │  │
  │           │  ├─ If Match: ✅
  │           │  │  ├─ Set session['user_id']
  │           │  │  ├─ Set session['username']
  │           │  │  ├─ Set session['role']
  │           │  │  ├─ Flash: "✅ Welcome back, {name}!"
  │           │  │  └─ Redirect: to /dashboard
  │           │  │
  │           │  └─ If No Match: ❌
  │           │     ├─ Flash: "❌ Invalid email or password!"
  │           │     └─ Redirect: back to /login
  │           │
  │           └─ Response: 302 Redirect
  │
  └─→ /dashboard (PROTECTED ROUTE)
      │
      ├─ Check: @login_required decorator ✅
      │   ├─ If session['user_id'] exists: ✅ Continue
      │   └─ If NOT exists: ❌ Redirect to /login
      │
      ├─ Display: dashboard.html ✅
      │   ├─ Navbar:
      │   │  ├─ Logo & Brand
      │   │  ├─ User Info (avatar + username)
      │   │  └─ Logout button
      │   │
      │   ├─ Main Content:
      │   │  ├─ Personalized greeting: "Welcome, {username}! 👋"
      │   │  ├─ Role badge: "Buyer Account" or "Seller Account"
      │   │  │
      │   │  └─ Role-Specific Quick Actions:
      │   │     ├─ If BUYER: Browse Items, Saved Items, My Orders
      │   │     └─ If SELLER: Post New Item, My Listings, Sales Analytics
      │   │
      │   └─ Statistics Cards (4):
      │      ├─ Total Orders
      │      ├─ Total Revenue
      │      ├─ Active Listings
      │      └─ Customer Ratings
      │
      └─ /logout (LOGOUT)
         │
         ├─ Clear session completely ✅
         ├─ Flash: "✅ Logged out successfully!"
         └─ Redirect: to /login ✅
```

---

## 🔌 API ENDPOINT REFERENCE

| Route | Method | Protected | Purpose | Form Fields |
|-------|--------|-----------|---------|-------------|
| `/` | GET | ❌ | Home page | - |
| `/register` | GET | ❌ | Show registration form | - |
| `/register` | POST | ❌ | Process registration | role, username, email, phone, password |
| `/login` | GET | ❌ | Show login form | - |
| `/login` | POST | ❌ | Process login | email, password |
| `/dashboard` | GET | ✅ | Show user dashboard | - |
| `/logout` | GET | ✅ | Clear session & logout | - |
| `/health` | GET | ❌ | Health check | - |

---

## 🗄️ DATABASE SCHEMA

```sql
TABLE: users
┌────────┬──────────────────┬──────┬─────┬──────────────────┐
│ Field  │ Type             │ Null │ Key │ Default          │
├────────┼──────────────────┼──────┼─────┼──────────────────┤
│ id     │ INT              │ NO   │ PRI │ AUTO_INCREMENT   │
│ role   │ ENUM(buyer,sell) │ NO   │     │ buyer            │
│ usrname│ VARCHAR(100)     │ NO   │ UNI │ NULL             │
│ email  │ VARCHAR(100)     │ NO   │ UNI │ NULL             │
│ phone  │ VARCHAR(20)      │ YES  │     │ NULL             │
│ password│ VARCHAR(255)    │ NO   │     │ NULL             │
│ created│ DATETIME         │ YES  │     │ CURRENT_TIMESTAMP│
└────────┴──────────────────┴──────┴─────┴──────────────────┘
```

**Password Storage Format:** `salt$hash` (e.g., `a1b2c3d4e5f6g7h8$9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z`)

---

## 🔐 SESSION MANAGEMENT

### Session Variables Set on Login:
```python
session['user_id']  = <id from users table>
session['username'] = <full name from users table>
session['role']     = 'buyer' or 'seller'
```

### Session Verification:
- ✅ Applied via `@login_required` decorator
- ✅ Checks for `session['user_id']` existence
- ✅ Redirects to `/login` if not authenticated
- ✅ Flash message: "Please login first!"

### Session Clearing:
- ✅ On `/logout`: `session.clear()`
- ✅ On browser close: Session expires

---

## 🎨 FRONTEND FORM FIELD MAPPING

### Registration Form (register.html)

| HTML Input | Backend | Type | Validation | Database |
|-----------|---------|------|-----------|----------|
| role (hidden) | request.form.get('role') | hidden | buyer/seller | role |
| username | request.form.get('username') | text | min 3 chars | username |
| email | request.form.get('email') | email | must be unique | email |
| phone | request.form.get('phone') | tel | optional | phone |
| password | request.form.get('password') | password | min 6 chars | password (hashed) |
| confirmPassword | (frontend only) | password | must match | - |

### Login Form (login.html)

| HTML Input | Backend | Type | Validation | Database |
|-----------|---------|------|-----------|----------|
| email | request.form.get('email') | email | must exist | email |
| password | request.form.get('password') | password | must match hash | password |

---

## 🔐 PASSWORD SECURITY

### Registration Process:
```python
1. User enters password: "MySecure123!"
2. Frontend validates:
   - Minimum 6 characters ✅
   - Strength indicator shown ✅
   - Must match confirm password ✅
3. Backend validation:
   - Check length >= 6 ✅
4. Password hashing:
   - Generate random salt (16 hex chars) ✅
   - Hash = SHA-256(salt + password) ✅
   - Store format: "{salt}${hash}" ✅
5. Database stores: "a1b2c3d4e5f6g7h8$9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z"
```

### Login Process:
```python
1. User enters password: "MySecure123!"
2. Backend queries: SELECT password FROM users WHERE email = %s
3. Retrieves stored: "a1b2c3d4e5f6g7h8$9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z"
4. Verify function:
   - Extract salt: "a1b2c3d4e5f6g7h8"
   - Calculate: SHA-256("a1b2c3d4e5f6g7h8" + "MySecure123!") 
   - Compare: hash matches ✅
5. If match: Create session + redirect to dashboard
6. If no match: Show error + stay on login
```

---

## ✅ CONNECTIVITY CHECKLIST

### Frontend ✅
- [x] register.html: Form with all fields, role selector, validation
- [x] login.html: Email/password form, validation, redirect handling
- [x] dashboard.html: Session variables used, role-specific content, logout
- [x] All form actions point to correct routes
- [x] All input names match backend expectations
- [x] JavaScript validation prevents empty submissions
- [x] Flash message containers present in all forms

### Backend ✅
- [x] Flask app initialized with secret key
- [x] All routes defined and functional
- [x] Database connection established with error handling
- [x] Password hashing implemented with salt
- [x] Password verification implemented
- [x] @login_required decorator applied to protected routes
- [x] Session management working (set/clear)
- [x] Error messages clear and helpful
- [x] Redirects working (302 status codes)
- [x] SQL injection prevented (parameterized queries)

### Database ✅
- [x] Database created: regear_db
- [x] Users table created with all columns
- [x] Email unique constraint enforced
- [x] Username unique constraint enforced
- [x] Auto-increment ID working
- [x] Timestamps auto-set on creation
- [x] Autocommit enabled for immediate saves

### Integration ✅
- [x] Registration → Database save → Success message → Redirect to login
- [x] Login → Database check → Session create → Redirect to dashboard
- [x] Dashboard → Session check → Role-based content → Logout clears session
- [x] Error messages displayed in all scenarios
- [x] No plaintext passwords stored
- [x] No SQL injection vulnerabilities
- [x] Session persists across page refreshes
- [x] Session clears on logout

---

## 🧪 TESTING QUICK START

### 1. Database Setup
```sql
CREATE DATABASE regear_db;
USE regear_db;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('buyer', 'seller') DEFAULT 'buyer',
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Start Server
```bash
python app.py
```

### 3. Test Flow
1. Register: http://localhost:5000/register
2. Login: http://localhost:5000/login
3. Dashboard: http://localhost:5000/dashboard
4. Logout: Click button on dashboard

### 4. Verify Database
```sql
SELECT * FROM users;
```

---

## 🚨 CRITICAL CONFIGURATION

### app.py
```python
app.secret_key = "regear_secret_key_secure"  # Change in production!
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
```

### Database Connection
```python
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shra@0303",  # Change in production!
    database="regear_db",
    autocommit=True
)
```

### Password Hashing
```python
# Uses SHA-256 with random salt
# Format: salt$hash (64 + 1 + 64 = 129 chars max)
```

---

## 🎯 DEPLOYMENT CHECKLIST

Before going to production:

- [ ] Change `app.secret_key` to random secure key
- [ ] Change database password to strong password
- [ ] Set `app.run(debug=False)`
- [ ] Use environment variables for secrets (not hardcoded)
- [ ] Enable HTTPS/SSL
- [ ] Implement rate limiting on login/register
- [ ] Add email verification
- [ ] Add password reset functionality
- [ ] Enable database backups
- [ ] Monitor error logs
- [ ] Test with load simulator
- [ ] Security audit (OWASP top 10)

---

## 📞 SUPPORT REFERENCE

### Common Error Messages & Solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| Database connection failed | MySQL not running | Start MySQL service |
| TemplateNotFound | Wrong template folder | Use `templetes/` not `templates/` |
| Invalid email or password | User doesn't exist | Register first |
| Email already registered | Duplicate email | Use different email |
| Username already taken | Duplicate username | Use different username |
| Session error | Secret key not set | Check app.secret_key |
| Form not submitting | JavaScript error | Check browser console |
| CSRF token missing | Session issue | Clear cookies, re-login |

---

**Status:** ✅ COMPLETE - All pages connected and tested
**Framework:** Flask + MySQL + Bootstrap
**Security:** Passwords hashed, SQL injection prevented, Session protected
**Ready for:** Testing and deployment
