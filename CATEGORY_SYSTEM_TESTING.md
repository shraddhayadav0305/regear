# Category System - Quick Testing Guide

## 🧪 Test the Complete Flow

### Prerequisites
- Server running: `python app.py` (should be running on port 5000)
- Database created and MySQL connection active
- User account created for testing

### Test Scenario 1: Browse All Categories

**Steps:**
1. Open browser: `http://localhost:5000/sell`
2. **Expected Result:** See all 16 categories in a grid layout
3. **Verify:**
   - All category cards visible with icons
   - Search box working at top
   - Categories show subcategory count

**Categories Should Show:**
- Mobiles (6 subcategories)
- Computers & Laptops (7)
- Cameras & Lenses (6)
- TVs, Video & Audio (7)
- Gaming & Entertainment (6)
- Kitchen & Appliances (9)
- Computer Accessories (9)
- Electronic Hardware (6)
- Cars (6)
- Properties (6)
- Jobs (6)
- Bikes (5)
- Commercial Vehicles & Spares (5)
- Furniture (6)
- Fashion (6)
- Books, Sports & Hobbies (6)

---

### Test Scenario 2: Search Categories

**Steps:**
1. On `/sell` page
2. Type "mobile" in search box
3. **Expected Result:** Only "Mobiles" category shows
4. Verify other categories are hidden
5. Clear search → all categories reappear

**Test searches:**
- "computer" → shows Computers & Laptops
- "furniture" → shows Furniture
- "games" → shows Gaming & Entertainment
- "xyz123" → shows no results

---

### Test Scenario 3: Select Category and See Subcategories

**Steps:**
1. On `/sell` page
2. Click "Mobiles" card
3. **Expected Result:** Redirected to `/subcategories?category=Mobiles`
4. See page title "Mobiles"
5. See 6 subcategory cards:
   - Smartphones
   - Feature Phones
   - Mobile Accessories
   - Phone Chargers
   - Screen Protectors
   - Phone Cases
6. Breadcrumb shows: Home > Sell > Mobiles
7. Back button visible and functional

**Test with different categories:**
- Click "Computers & Laptops" → should show 7 subcategories
- Click "Kitchen & Appliances" → should show 9 subcategories
- Click "Bikes" → should show 5 subcategories

---

### Test Scenario 4: Select Subcategory (Requires Login)

**Steps:**
1. On subcategories page for any category
2. Click a subcategory card (e.g., "Smartphones")
3. **Expected Behavior:**
   - If NOT logged in → Redirected to `/login`
   - If logged in → Redirected to `/post-ad-form`

**To test with login:**
1. Register new account at `/register` (choose "seller" role)
2. Login at `/login`
3. Navigate to `/sell` again
4. Click category → see subcategories
5. Click subcategory → redirected to `/post-ad-form`

---

### Test Scenario 5: Verify Category is Prefilled in Ad Form

**Steps:**
1. Complete Test Scenario 4 (login and select Mobiles > Smartphones)
2. You should be on `/post-ad-form` page
3. Verify the form has:
   - Category field prefilled: "Mobiles"
   - Subcategory field prefilled: "Smartphones"

**Fill the form:**
1. Ad Title: "iPhone 13 Pro - Like New"
2. Condition: "Used"
3. Description: "Excellent condition, minimal scratches"
4. Price: "35000"
5. Location: "Mumbai"
6. Phone: "9876543210"
7. Click "Post Ad"

**Expected Result:** 
- Flash message: "✅ Ad posted successfully!"
- Redirected to `/my-listings`
- New listing appears with category "Mobiles" and subcategory "Smartphones"

---

### Test Scenario 6: Verify Database Entry

**Steps:**
1. After posting an ad (Test Scenario 5)
2. Open MySQL command line or database tool
3. Run query:
```sql
SELECT id, user_id, category, subcategory, title, price, status 
FROM listings 
ORDER BY id DESC 
LIMIT 1;
```

**Expected Result:**
```
| id | user_id | category | subcategory | title                      | price | status |
|----|---------|----------|-------------|----------------------------|-------|--------|
| 1  | 1       | Mobiles  | Smartphones | iPhone 13 Pro - Like New   | 35000 | active |
```

---

### Test Scenario 7: Test Back Navigation

**Steps:**
1. On `/sell` → click a category
2. On subcategories page → click "Back to Categories" button
3. **Expected:** Returned to `/sell` page with all categories visible

**Alternative:**
1. On subcategories page → click breadcrumb "Sell"
2. **Expected:** Also returns to categories page

---

### Test Scenario 8: Responsive Design (Mobile)

**Steps:**
1. Open `/sell` in browser
2. Reduce window width to simulate mobile (375px width)
3. **Verify:**
   - Categories grid adjusts to 1-2 columns
   - Search box still functional
   - Cards are clickable
   - Text is readable
   - No overflow issues

4. Repeat on `/subcategories` page

---

### Test Scenario 9: API Endpoint Testing

**Using curl or Postman:**

**Test `/api/categories` endpoint:**
```bash
curl http://localhost:5000/api/categories
```

**Expected Response:**
```json
{
  "Mobiles": {
    "icon": "📱",
    "subcategories": [
      "Smartphones",
      "Feature Phones",
      "Mobile Accessories",
      ...
    ]
  },
  "Computers & Laptops": {
    ...
  },
  ...
}
```

**Test `/save-category` endpoint:**
```bash
curl -X POST http://localhost:5000/save-category \
  -H "Content-Type: application/json" \
  -d '{"category":"Mobiles","subcategory":"Smartphones"}'
```

**Expected Response (without login):**
```json
{
  "success": false,
  "message": "Please login first"
}
```

**With login (after setting session cookie):**
```json
{
  "success": true,
  "message": "Category saved",
  "redirect": "/post-ad-form"
}
```

---

## 🐛 Troubleshooting

### Issue: Categories not showing on `/sell`

**Solution:**
1. Check server logs for errors
2. Verify `/api/categories` endpoint returns data
3. Open browser console (F12) for JavaScript errors
4. Ensure Bootstrap and Font Awesome CDN links are loaded

### Issue: Subcategories page shows blank

**Solution:**
1. Verify category parameter in URL matches exactly (case-sensitive)
2. Check if Flask is rendering the template correctly
3. Look at page source (Ctrl+U) to see if Jinja2 variables are being replaced

### Issue: "Please login first" when selecting subcategory

**Solution:**
1. This is expected behavior - login first
2. Register at `/register`
3. Login at `/login`
4. Try again

### Issue: Ad form not prefilled with category

**Solution:**
1. Verify session variables are set: `session['selected_category']` should exist
2. Check Flask session timeout settings
3. Clear browser cookies and try again
4. Check `addpost.html` for form field names

---

## ✅ Checklist for Verification

- [ ] All 16 categories display on `/sell` page
- [ ] Search functionality filters categories correctly
- [ ] Clicking category shows correct subcategories
- [ ] Breadcrumb navigation works
- [ ] Back button returns to categories
- [ ] Subcategory selection saves to session (check with login)
- [ ] Redirects to ad form with prefilled category
- [ ] Ad form submits successfully
- [ ] New listing appears in database with correct category
- [ ] Responsive design works on mobile (375px width)
- [ ] `/api/categories` endpoint returns valid JSON
- [ ] All 16 categories have correct number of subcategories

---

## 📊 Test Results Template

```
Test Date: ___________
Tester Name: ___________
Browser: ___________
Device: ___________

Test Scenario 1 (Browse Categories): ✓ Pass / ✗ Fail
Test Scenario 2 (Search): ✓ Pass / ✗ Fail
Test Scenario 3 (Select Category): ✓ Pass / ✗ Fail
Test Scenario 4 (Login & Select Sub): ✓ Pass / ✗ Fail
Test Scenario 5 (Prefilled Form): ✓ Pass / ✗ Fail
Test Scenario 6 (Database Entry): ✓ Pass / ✗ Fail
Test Scenario 7 (Back Navigation): ✓ Pass / ✗ Fail
Test Scenario 8 (Responsive): ✓ Pass / ✗ Fail
Test Scenario 9 (API Testing): ✓ Pass / ✗ Fail

Overall Result: ✓ All Pass / ✗ Some Failed

Notes:
_________________________________________________
_________________________________________________
```

---

## 🎯 Success Criteria

The category system is working correctly when:
1. ✅ All 16 categories visible on `/sell`
2. ✅ Search filters categories in real-time
3. ✅ Category click shows relevant subcategories
4. ✅ Login required to select subcategory
5. ✅ Ad form prefilled with selected category
6. ✅ Submitted ad has correct category in database
7. ✅ No JavaScript console errors
8. ✅ Responsive on mobile devices
9. ✅ All links and navigation working
10. ✅ Proper error messages shown when needed
