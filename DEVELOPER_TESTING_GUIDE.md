# ReGear OLX Model - Developer Testing Guide

## 🚀 Quick Start for Testing

### 1. Run Database Migration
```bash
# From project root directory
python migration_olx_model.py

# Expected output:
# ✅ Database migration completed successfully!
```

### 2. Start Flask Server
```bash
python app.py
# Server running on http://localhost:5000
```

### 3. Test Registration
```
URL: http://localhost:5000/register
User: test_user
Email: test@example.com
Phone: 9876543210
Password: Test@1234
```

Should redirect to `/dashboard` after registration.

---

## 🧪 Testing Checklist

### Authentication Flow
- [ ] Register new user → Create new test user
- [ ] Verify user record created in DB with role='user'
- [ ] Login with test user
- [ ] Verify session variables set correctly
- [ ] Logout → Verify redirect to home

### Product Posting
- [ ] Login as test user
- [ ] Navigate to `/sell`
- [ ] Select category & subcategory
- [ ] Fill out product details form
- [ ] Upload product images (1-5 JPGs)
- [ ] Submit form
- [ ] Verify product appears in `/my-listings`
- [ ] Verify `expires_date` is 5 days from now

### Dashboard
- [ ] Verify all stats display correctly
- [ ] Check active_listings count
- [ ] Check expired_listings count
- [ ] Check sold_listings count
- [ ] Verify recent listings show

### Boost Flow (Simulate Expiration)
```sql
-- Manually set product to expired
UPDATE listings SET expires_date=NOW() WHERE id=1;
```

Then:
- [ ] View my-listings
- [ ] Product shows in "Expired" section
- [ ] "Boost" button shows
- [ ] Click boost
- [ ] Verify package options display
- [ ] Select a package and submit

### Mark as Sold
- [ ] In dashboard, click "Mark Sold" on active product
- [ ] Verify AJAX call succeeds
- [ ] Product moves to "Sold" section
- [ ] User's completed_sales count increases

---

## 📊 Database Validation Queries

### Check User Creation
```sql
SELECT id, username, email, role, full_name FROM users WHERE email='test@example.com';
```

Expected: role should be 'user', full_name should be populated

### Check Listing Details
```sql
SELECT id, user_id, title, posted_date, expires_date, listing_type, is_sold FROM listings 
WHERE user_id=(SELECT id FROM users WHERE email='test@example.com');
```

Expected: `listing_type` = 'free_trial', `is_sold` = FALSE

### Check Product Boosts
```sql
SELECT * FROM product_boosts WHERE user_id=1;
```

This should be empty initially, populated after boost purchase.

### Verify Expiration Date Logic
```sql
SELECT id, title, expires_date, DATEDIFF(expires_date, NOW()) as days_remaining
FROM listings WHERE user_id=1;
```

Expected: days_remaining should be ~5 or less

---

## 🔧 Testing Expiration System

### Manual Expiration Test
```bash
# Trigger expiration via API
curl -X POST http://localhost:5000/api/expire-listings
```

Expected response:
```json
{
  "success": true,
  "message": "Expired 0 listings"  // or number of actually expired
}
```

### Force Expiration for Testing
```sql
-- Set expires_date to past
UPDATE listings SET expires_date=DATE_SUB(NOW(), INTERVAL 1 DAY) WHERE id=1;

-- Then hit the expire API
curl -X POST http://localhost:5000/api/expire-listings
```

---

## 🧬 Testing API Endpoints

### Check Expiration Status
```bash
curl -X POST http://localhost:5000/api/check-expiration \
  -H "Content-Type: application/json" \
  -d '{"listing_id": 1}'
```

Should return status: active/expired/sold

### Mark Product as Sold
```bash
curl -X POST http://localhost:5000/listing/1/mark-sold \
  -H "Content-Type: application/json"
```

Expected: Product is_sold flag set to TRUE

---

## 🐛 Common Testing Issues & Solutions

### Issue: Login redirects to home instead of dashboard
**Problem:** User role might not be 'user'
**Solution:**
```sql
UPDATE users SET role='user' WHERE id=1;
```

### Issue: Product not showing 5-day expiration
**Problem:** expires_date might not have been set
**Solution:**
```sql
UPDATE listings SET expires_date=DATE_ADD(NOW(), INTERVAL 5 DAY) 
WHERE expires_date IS NULL;
```

### Issue: Dashboard shows 0 stats
**Problem:** Stats query might be failing
**Solution:** Check app.py logs
```bash
tail -f app.log  # If logging is enabled
```

### Issue: Templates not found (404)
**Problem:** Template files may not exist or paths wrong
**Solution:**
```bash
# Verify template files exist
ls -la templates/ | grep -E "register_unified|dashboard_unified|post_product|boost_listing"
```

### Issue: Image upload fails
**Problem:** Upload directory doesn't exist
**Solution:**
```bash
mkdir -p static/uploads/products
chmod 755 static/uploads
```

---

## 📈 Performance Testing

### Load Test Registration
```bash
# Test registering multiple users (be careful!)
for i in {1..10}; do
  curl -X POST http://localhost:5000/register \
    -d "full_name=User$i&email=user$i@test.com&phone=987654321$i&password=test123&password_confirm=test123"
done
```

### Load Test Product Posting
```bash
# Test posting multiple products (requires login)
for i in {1..5}; do
  curl -X POST http://localhost:5000/post-ad-form \
    -F "category=Electronics" \
    -F "subcategory=Phone" \
    -F "title=Product $i" \
    -F "description=Test product" \
    -F "price=5000" \
    -F "location=Mumbai" \
    -F "condition=New" \
    -F "photos=@test.jpg"
done
```

---

## 🔍 Database Monitoring

### Check Database Size
```sql
SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.tables WHERE table_schema = 'regear_db'
ORDER BY size_mb DESC;
```

### Check Growth of New Tables
```sql
SELECT 'product_boosts' as table_name, COUNT(*) as row_count FROM product_boosts
UNION
SELECT 'product_reviews', COUNT(*) FROM product_reviews
UNION
SELECT 'product_reports', COUNT(*) FROM product_reports
UNION
SELECT 'chats', COUNT(*) FROM chats;
```

### Monitor Active Listings
```sql
SELECT 
  DATE(posted_date) as posted_on,
  COUNT(*) as posted_count,
  SUM(CASE WHEN is_sold THEN 1 ELSE 0 END) as sold,
  SUM(CASE WHEN is_sold THEN 0 ELSE 1 END) as unsold
FROM listings
GROUP BY DATE(posted_date)
ORDER BY posted_on DESC;
```

---

## 📄 Testing Log Checklist

Create `test_results.txt` to document:

```
=== ReGear OLX Model - Testing Results ===
Date: 2026-03-04

REGISTRATION:
[ ] New user creation: PASS/FAIL
[ ] Email validation: PASS/FAIL
[ ] Phone validation: PASS/FAIL
[ ] Role assignment (user): PASS/FAIL

POSTING:
[ ] Product created: PASS/FAIL
[ ] Expiration set (5 days): PASS/FAIL
[ ] Images uploaded: PASS/FAIL
[ ] Dashboard stats update: PASS/FAIL

BOOST:
[ ] Package display: PASS/FAIL
[ ] Package selection: PASS/FAIL
[ ] Boost record creation: PASS/FAIL

DATABASE:
[ ] New tables created: PASS/FAIL
[ ] Columns added: PASS/FAIL
[ ] Queries functional: PASS/FAIL

NOTES:
...

SIGNED: [Your Name]
```

---

## 🚨 Production Checklist

Before going live:

- [ ] All templates tested on mobile devices
- [ ] Database backup created
- [ ] Expiration cron job scheduled
- [ ] Error logging enabled
- [ ] Analytics configured
- [ ] Support contact added to templates
- [ ] Email notifications tested (future feature)
- [ ] Security headers configured
- [ ] HTTPS enabled
- [ ] Database credentials secured (env vars)
- [ ] File upload directory protected
- [ ] Session timeout configured
- [ ] Rate limiting implemented (future)
- [ ] User agreement/ToS updated
- [ ] Privacy policy updated

---

## 📱 Mobile Testing

Test on mobile devices:
- iPhone (Safari)
- Android (Chrome)
- Desktop (Chrome, Firefox, Safari)

Specifically check:
- [ ] Registration form responsive
- [ ] Product posting on mobile
- [ ] Image upload on mobile
- [ ] Dashboard layout on small screens
- [ ] Buttons click-able (48px minimum)
- [ ] Touch interactions smooth

---

## 🔐 Security Testing

- [ ] SQL injection attempts on forms
- [ ] XSS attempts in product description
- [ ] CSRF token validation
- [ ] Session hijacking prevention
- [ ] Password hashing verification
- [ ] File upload validation
- [ ] Unauthorized access attempts

---

## 📞 Support & Documentation

If issues arise during testing:

1. Check error logs: `app.py` should log errors
2. Verify database: Run SQL validation queries above
3. Check migrations: Confirm all tables/columns exist
4. Review templates: Ensure all files present

---

## ✅ Sign-Off Checklist

Once testing complete:

```
This system has been tested and verified working:

[ ] Database migration successful
[ ] User registration working
[ ] Product posting working
[ ] Dashboard functional
[ ] Boost system functional
[ ] Expiration system working
[ ] Mobile responsive
[ ] Security validated

Ready for: [DEVELOPMENT / STAGING / PRODUCTION]

Tested By: _______________
Date: _______________
Notes: _______________
```

---

**Happy Testing! 🚀**

For issues, refer to `REGEAR_REDESIGN_COMPLETE.md` for architecture details.

