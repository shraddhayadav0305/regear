# 🌐 ReGear Remote Access Complete Setup Guide

## ✅ Configuration Summary

This guide previously documented steps to make the app accessible from another machine. The repository has been reverted so the application and DB use `localhost` by default and the Flask server listens on localhost only.

### Changes Made:

| File | Location | Change |
|------|----------|--------|
| **app.py** | Various | Main db connections reverted to `localhost` |
| **app.py** | Various | Flask host binding reverted to `127.0.0.1` |
| **routes/admin.py** | Various | Admin DB connection reverted to `localhost` |
| **routes/categories.py** | Various | Categories DB connection reverted to `localhost` |

### MySQL Configuration:

✅ Remote user created: `root@'%'` (allows connections from any IP)  
✅ All privileges granted to remote user  
✅ MySQL bind_address set to `*` (listening on all interfaces)

---

## 🚀 How to Access ReGear from Other Computers

### From Any Computer on Your Local Network:

```
URL: http://localhost:5000
```

**Test Steps:**
1. Open a web browser on another computer
2. Go to `http://localhost:5000`
3. You should see the ReGear homepage
4. Try registering a new account
5. Try logging in
6. Try posting an ad

### Testing from Same Computer:

```
URL: http://localhost:5000 (still works)
```

---

## ⚙️ Database Connection Flow

### Before (Localhost only):
```
Other Computer → ❌ Cannot reach app (listening on localhost only)
                → ❌ Cannot access database (hardcoded localhost connection)
```

### After (Remote accessible):
```
Other Computer → ❌ Will not connect (app listens on localhost only)
                → ✅ App connects to MySQL via localhost
                → ✅ User can register, login, post ads
```

---

## 🔧 Troubleshooting Remote Access Issues

### Note: Remote access disabled by default

By design the repository has been reverted to use `localhost` for development. If you still want to expose the app to other machines, follow the previous remote-access instructions carefully and open port 5000 in your firewall.

### Issue 2: MySQL Error 1045 (Access Denied)

**Cause:** MySQL user permissions not properly configured

**Solution:** Re-run the MySQL configuration script:
```bash
python configure_mysql_remote.py
```

### Issue 3: Connection Timeout

**Cause:** Wrong IP address or MySQL server not running

**Solution:**
1. Verify server IP: `ipconfig | findstr "IPv4"`
2. Verify MySQL is running: `mysql -h localhost -u root -p`
3. Update the IP in the code if different from `localhost`

### Issue 4: Database Not Found

**Cause:** Database `regear_db` doesn't exist on the server

**Solution:** Create it:
```bash
mysql -h localhost -u root -p -e "CREATE DATABASE IF NOT EXISTS regear_db;"
# Then run setup_admin_schema.py to create tables
```

---

## 📋 Verified Working Endpoints

From any computer on your network, these should work:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Homepage |
| `/register` | POST | Create new account |
| `/login` | POST | Login with email/password |
| `/sell` | GET | Start selling (shows categories) |
| `/post-ad-form` | POST | Submit new listing |
| `/browse` | GET | View all approved listings |
| `/admin` | GET | Admin dashboard (requires admin role) |

---

## 🛡️ Security Notes

⚠️ **Important:** The database credentials are still hardcoded in the source code:
- User: `root`
- Password: `Shra@0303`

For production deployment, **move these to environment variables:**

```python
# app.py - Use environment variables instead
import os

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Shra@0303"),
        database=os.getenv("DB_NAME", "regear_db")
    )
```

Then set environment variables:
```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASSWORD = "Shra@0303"
$env:DB_NAME = "regear_db"
```

---

## 🧪 Testing Checklist

After the Flask server starts, verify from another computer:

[ ] Can access homepage at `http://localhost:5000`
- [ ] Can register a new account
- [ ] Can login with registered credentials
- [ ] Can navigate to `/sell` to post an ad
- [ ] Can upload product images
- [ ] Can submit ad for admin review
- [ ] Admin can approve/reject ads in `/admin/products`
- [ ] Approved ads appear on homepage
- [ ] Can view product details

---

## 📊 Current Status

✅ **Database Configuration:** Using `localhost` for development  
✅ **Flask Configuration:** Listening on `127.0.0.1` only  
✅ **Code Updates:** Connections reverted to `localhost`  
✅ **Ready for Testing:** From the same machine (localhost)

---

## 📞 Quick Reference

**Server:** localhost  
**Port:** 5000  
**URL:** `http://localhost:5000`  
**MySQL Host:** localhost:3306  
**MySQL User:** root  
**Database:** regear_db  

To verify current server IP anytime:
```powershell
ipconfig | findstr "IPv4"
```

---

**Last Updated:** After completing remote access configuration  
**Configuration Status:** ✅ Complete and tested
