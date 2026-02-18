# 📋 ReGear Sell Flow - Like OLX

## Complete User Journey

### Step 1: Categories Page (/sell)
- User clicks "Sell" in navbar
- Sees all 16 main categories with emojis and icons
- Each category shows:
  - ✅ Category name (e.g., "Mobiles", "Laptops & Computers")
  - ✅ Emoji icon (📱, 💻, etc.)
  - ✅ First 3 subcategories preview
  - ✅ Total count of subcategories
- User can search categories in real-time
- **User clicks on a category → Proceeds to Step 2**

### Step 2: Subcategories Page (/subcategories?category=X)
- User sees all subcategories for selected category
- Each subcategory is a clickable card
- Example for "Mobiles":
  - iPhone 6, iPhone 7, iPhone 8, iPhone X, iPhone 11, iPhone 12, etc.
  - Samsung Galaxy S6, S7, S8, S9, S10, S20, S21, S22, S23, etc.
  - OnePlus, Xiaomi, Realme, Oppo, Vivo, etc.
- **User clicks on subcategory → Proceeds to Step 3**

### Step 3: Save Category & Redirect
- When user clicks subcategory:
  1. Sends POST to `/save-category` with:
     ```json
     {
       "category": "Mobiles",
       "subcategory": "iPhone 13"
     }
     ```
  2. Saves to session
  3. Returns redirect URL: `/post-ad-form`
  4. JavaScript redirects to post form

### Step 4: Post Ad Form (/post-ad-form)
The form has 4 main sections:

#### 📝 Section 1: Product Details
- **Category & Subcategory**: (Auto-filled, disabled)
  ```
  Primary Category: Mobiles
  Sub Category: iPhone 13
  ```
- **Brand Selector** (for mobile category):
  - Samsung, Nokia, Asus, iPhone, Micromax, Sony, HTC, BlackBerry, etc.
- **Ad Title** (required)
  - Max 80 characters
  - Example: "iPhone 13 Pro Max 256GB - Excellent Condition"
- **Condition** (required, radio buttons):
  - Brand New - Sealed & unopened
  - Like New - Unused, minimal or no signs of use
  - Used - Good - Works perfectly, minor cosmetic wear
  - Used - Fair - Works well, visible signs of wear
- **Description** (required)
  - Max 2000 characters
  - Scrollable text area
  - Hints about what to include

#### 💰 Section 2: Price
- **Price in INR** (required)
  - Input with ₹ symbol
- **Price is negotiable** (checkbox)

#### 📸 Section 3: Photos
- Drag & drop or click to upload
- Up to 8 photos
- Supported: JPG, PNG
- Max 5MB each
- Shows preview thumbnails
- Remove button on each preview

#### 👤 Section 4: Your Details
- **Full Name**: (Auto-filled from session, disabled)
- **Phone Number** (required)
- **Email** (optional)
- **Location** (optional, shows city/area)

#### ✅ Submit
- **"Post Your Ad Now"** button
- Shows loading state on submit
- **"Cancel"** button → goes back to /sell

### Step 5: Admin Review
After posting:
1. Ad status set to: `approval_status='pending'`
2. User sees: "Your ad has been submitted successfully! It's now pending admin review."
3. Redirects to `/my-listings` (user's dashboard)
4. Admin goes to `/admin/products`
5. Admin sees pending ads first (sorted by approval_status)
6. Admin can:
   - ✅ Approve (status → 'approved', shows on homepage)
   - ❌ Reject (status → 'rejected', with reason)

### Step 6: Product Live
Once approved:
1. Product appears on homepage (`/`)
2. Shows in "Recent Listings" section
3. Visible in `/browse` page
4. Users can click to view details (`/listing/<id>`)

---

## 🛠️ Technical Flow

```
User clicks "Sell"
        ↓
GET /sell → categories.html (displays all categories)
        ↓
User clicks category
        ↓
GET /subcategories?category=CATEGORY_NAME → subcategories.html
        ↓
User clicks subcategory
        ↓
POST /save-category (with JSON)
        ↓
Session saves: selected_category, selected_subcategory
        ↓
Return: {"success": true, "redirect_url": "/post-ad-form"}
        ↓
GET /post-ad-form → addpost.html (category pre-filled)
        ↓
User fills form and uploads photos
        ↓
POST /post-ad-form (multipart form data)
        ↓
Insert to DB: listing.approval_status = 'pending'
        ↓
Flash: "Your ad has been submitted successfully!"
        ↓
Redirect to /my-listings
        ↓
Admin reviews at /admin/products
        ↓
Approve → approval_status = 'approved'
        ↓
Product visible on homepage & /browse
```

---

## ✨ Features Implemented

✅ Multi-step category flow  
✅ Subcategory selection  
✅ Pre-filled category display  
✅ Brand selector for mobiles  
✅ Multiple condition options  
✅ Photo upload (up to 8)  
✅ Seller contact details  
✅ Admin approval workflow  
✅ Pending → Approved → Live  
✅ Product display on homepage  
✅ Search functionality  
✅ Responsive design (OLX-like)  
✅ All navbar links using Flask routes  
✅ Proper error handling and validation  

---

## 🧪 Testing Checklist

- [ ] Can navigate: /sell → categories
- [ ] Category search works
- [ ] Click category → shows subcategories
- [ ] Click subcategory → redirects to post form
- [ ] Form shows correct category/subcategory
- [ ] Brand selector appears for mobiles
- [ ] Can upload photos
- [ ] Form validates all required fields
- [ ] Can submit ad
- [ ] See success message
- [ ] Redirects to /my-listings
- [ ] Ad shows approval_status = 'pending'
- [ ] Admin sees it in /admin/products
- [ ] Admin can approve
- [ ] Ad appears on homepage
- [ ] Ad appears on /browse

---

## 📱 Mobile Responsive

- All pages responsive (tested on Bootstrap 5)
- Touch-friendly buttons and inputs
- Optimized for small screens
- Mobile-first design approach

