# Seller Registration & Payment System Implementation

## Implementation Complete ✅

A full OLX-style seller registration and subscription payment system has been implemented for ReGear.

---

## System Architecture

### Phase 1: Seller Registration (Updated)
- **Route:** GET/POST `/register`
- **Changes:**
  - Removed package selection from registration form
  - Sellers now register with basic info only (name, email, password, phone)
  - Sellers created with `seller_active = 0` (inactive until payment)
  - After registration, sellers auto-logged in and redirected to `/select-package`

### Phase 2: Package Selection (NEW)
- **Route:** GET/POST `/select-package`
- **Template:** `select_package.html`
- **Features:**
  - Displays 3 pricing tiers in modern card layout:
    - **Basic**: ₹99/month (5 products, standard visibility)
    - **Standard**: ₹199/month (15 products, priority listing, email support) - *Most Popular*
    - **Premium**: ₹399/month (unlimited products, featured badge, analytics)
  - Form submission saves selected plan to session
  - Redirects to payment page

### Phase 3: Payment Processing (NEW)
- **Route:** GET/POST `/payment`
- **Template:** `payment.html`
- **Features:**
  - Displays selected plan details
  - Calculates and shows GST (18%)
  - Total amount = Amount + GST
  - Payment method dropdown (UPI/Card/Net Banking)
  - POST submission triggers payment recording

### Phase 4: Post-Payment Activation (NEW)
- **Route:** GET `/seller-dashboard`
- **Template:** `seller_dashboard.html`
- **On payment success:**
  - Updates user record: `seller_active = 1`
  - Sets `subscription_start` = current timestamp
  - Sets `subscription_end` = current timestamp + 30 days
  - Records payment in `seller_payments` table
  - Shows success confirmation
  - Links to main dashboard

---

## Key Components Added

### Backend Routes

```python
@app.route("/select-package", methods=["GET", "POST"])
# Show 3 package options, save selection to session

@app.route("/payment", methods=["GET", "POST"])
# Show payment details with GST calculation
# On POST: Save subscription data to users table

@app.route("/seller-dashboard")
# Show confirmation and subscription details

def check_seller_status()
# Helper function - checks if seller has active subscription
# Used in post_ad_form to enforce payment requirement
```

### Database Changes

**New columns in `users` table:**
- `seller_active` (TINYINT) - 0=inactive, 1=active
- `subscription_start` (TIMESTAMP) - When plan started
- `subscription_end` (TIMESTAMP) - When plan expires

**New table: `seller_payments`**
```sql
CREATE TABLE seller_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    plan VARCHAR(50),
    amount DECIMAL(10,2),
    gst DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
)
```

### Updated Routes

**POST /register**
- No longer accepts package selection
- Auto-logs in seller after registration
- Redirects to `/select-package` for sellers
- Creates user with `seller_active = 0`

**POST /post-ad-form**
- Now checks `check_seller_status()` before proceeding
- If subscription inactive: redirects to `/select-package` with error message
- If subscription expired: redirects to `/select-package` with renewal message

---

## Templates Created

### 1. `select_package.html`
- Modern 3-column pricing card layout
- Highlights "Most Popular" plan
- Bootstrap responsive design
- Shows features list for each plan

### 2. `payment.html`
- Clean payment summary card
- Shows: Plan name, amount, GST, total
- Payment method dropdown
- "100% Secure Payment" badge
- "Pay Now" button

### 3. `seller_dashboard.html`
- Confirms subscription activation
- Shows: Plan name, validity dates, status
- Links to main dashboard
- Displays renewal option if expired

---

## Admin Dashboard Enhancements

**Updated `/admin/users` page:**
- New columns: `seller_active`, `subscription_start`, `subscription_end`

**Updated `/admin/user/<id>` page:**
- Shows subscription status for sellers
- **NEW SECTION:** Payment History table
- Shows all past payments with:
  - Plan name
  - Amount & GST breakdown
  - Payment method
  - Payment date
- Extension form to manually extend subscription

### Admin Helper Function
```python
@admin_bp.route("/admin/user/<id>/extend-subscription", methods=["POST"])
def extend_subscription()
# Admin can manually extend seller subscription by N days
```

---

## Restriction Logic

### ✅ Active Subscription Required for Sellers

**Check in `post_ad_form`:**
```python
allowed, msg = check_seller_status()
if not allowed:
    flash(msg, "error")
    return redirect(url_for('select_package'))
```

**Conditions:**
- `seller_active` must be 1
- `subscription_end` must be future date
- If payment required: error message directs to `/select-package`
- If expired: error message offers renewal

---

## Payment Gateway Integration

Currently simulated with offline processing. To integrate real payment:

### Razorpay Integration Example
```python
@app.route("/payment", methods=["POST"])
def payment():
    # Redirect to Razorpay checkout page
    # Razorpay calls webhook on success
    # Webhook updates seller_active=1
```

### Webhook Handler
```python
@app.route("/webhook/payment-success", methods=["POST"])
def payment_webhook():
    # Verify Razorpay signature
    # Update user.seller_active = 1
    # Mark payment as verified in seller_payments
```

---

## User Journey

```
1. User clicks "Register as Seller"
   ↓
2. Register form (basic info only)
   ↓
3. POST /register → Auto-login as seller
   ↓
4. Redirect to /select-package
   ↓
5. Choose plan (Basic/Standard/Premium)
   ↓
6. POST -> session['selected_plan'] set
   ↓
7. Redirect to /payment
   ↓
8. View payment details with GST
   ↓
9. Choose payment method, click "Pay Now"
   ↓
10. POST /payment → Update user subscription
    ↓
11. seller_active = 1
    subscription_start = NOW
    subscription_end = NOW + 30 days
    ↓
12. Redirect to /seller-dashboard (success confirmation)
    ↓
13. Seller can now POST /post-ad-form
    ↓
14. check_seller_status() allows listing → create ad
```

---

## Testing

### Register as Seller
1. Go to `/register`
2. Select "Seller" role
3. Fill: name, email, password, phone
4. Click "Register"
5. Auto-redirected to `/select-package`

### Select Plan
1. On `/select-package`
2. Click "Select Plan" on any card
3. Redirected to `/payment`

### Complete Payment
1. On `/payment`
2. Select payment method
3. Click "Pay Now"
4. Redirected to `/seller-dashboard` (success shown)
5. Subscription active for 30 days

### Post Listing
1. Login as seller
2. Click "Sell Item"
3. Redirected to `/select-package` if inactive (with error)
4. If active: can fill listing form

---

## Admin Features

### View Seller Subscriptions
- `/admin/users` shows seller_package and active status
- `/admin/user/<id>` shows detailed subscription info

### View Payment History
- `/admin/user/<id>` includes Payment History section
- Shows all transactions with amounts & dates

### Extend Subscription
- Admin dropdown on user detail page
- Extend by N days through simple form

---

## Configuration

**Package Definitions (in app.py):**
```python
packages = [
    {"key": "basic", "name": "Basic Plan", "price": 99, ...},
    {"key": "standard", "name": "Standard Plan", "price": 199, ...},
    {"key": "premium", "name": "Premium Plan", "price": 399, ...}
]
```

**Subscription Duration:**
- Currently: 30 days per purchase
- Modify line in `payment()` POST handler:
  ```python
  end = start + timedelta(days=30)  # Change 30 to desired days
  ```

---

## Files Modified/Created

### New Files
- `templates/select_package.html` - Package selection page
- `templates/payment.html` - Payment confirmation
- `templates/seller_dashboard.html` - Success & subscription view
- `setup_seller_subscription.py` - Database migration script

### Modified Files
- `app.py` - Added 3 new routes + check_seller_status() helper
- `templates/register.html` - Removed package selection dropdown
- `routes/admin.py` - Enhanced user detail view with payments
- `templates/admin/admin_user_detail.html` - Added payment history section

---

## Next Steps for Production

1. **Real Payment Gateway:**
   - Integrate Razorpay/PayU/CCAvenue
   - Add webhook handlers
   - Add payment verification

2. **Email Notifications:**
   - Send confirmation email after successful payment
   - Send renewal reminders before expiry
   - Send invoice PDF

3. **Automatic Renewal:**
   - Payment retry before expiry
   - Automatic suspension if renewal fails

4. **Analytics:**
   - Monthly/annual revenue reports
   - Seller retention metrics
   - Payment failure analysis

5. **Refunds & Disputes:**
   - Refund request handling
   - Dispute resolution workflow
   - Payment reversals

---

## Status: READY FOR TESTING ✅

All components implemented and database configured. System is live at:
- Seller Registration: http://localhost:5000/register
- Package Selection: http://localhost:5000/select-package
- Payment: http://localhost:5000/payment
- Seller Dashboard: http://localhost:5000/seller-dashboard
- Admin: http://localhost:5000/admin/users
