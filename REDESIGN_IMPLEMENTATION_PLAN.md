# ReGear System Redesign - Implementation Plan (OLX Model)

## Overview
Transform from seller/buyer separation + forced payment model to unified user system with free trial selling and smart monetization.

---

## Phase 1: Database Schema Updates

### 1. Update `users` Table
```sql
ALTER TABLE users
ADD COLUMN IF NOT EXISTS phone VARCHAR(20) AFTER email,
ADD COLUMN IF NOT EXISTS full_name VARCHAR(255) AFTER username,
MODIFY COLUMN role ENUM('user', 'admin', 'blocked') DEFAULT 'user',
ADD COLUMN IF NOT EXISTS total_listings INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS completed_sales INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS seller_rating DECIMAL(3,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_rating_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

### 2. Update `listings` Table
```sql
ALTER TABLE listings
ADD COLUMN IF NOT EXISTS posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS expires_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS is_sold BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS sold_date TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS view_count INT DEFAULT 0,
MODIFY COLUMN status ENUM('active', 'expired', 'sold', 'boosted', 'featured', 'archived') DEFAULT 'active',
ADD COLUMN IF NOT EXISTS boost_type VARCHAR(50) NULL,
ADD COLUMN IF NOT EXISTS boost_expires_date TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS listing_type ENUM('free_trial', 'boosted', 'featured', 'premium') DEFAULT 'free_trial';
```

### 3. Create `product_boosts` Table
```sql
CREATE TABLE IF NOT EXISTS product_boosts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT NOT NULL,
  user_id INT NOT NULL,
  boost_type VARCHAR(50) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  days_active INT NOT NULL,
  purchased_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_date TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 4. Create `product_reviews` Table
```sql
CREATE TABLE IF NOT EXISTS product_reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT NOT NULL,
  buyer_id INT NOT NULL,
  seller_id INT NOT NULL,
  rating INT CHECK (rating >= 1 AND rating <= 5),
  review_text TEXT,
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
  FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 5. Create `product_reports` Table
```sql
CREATE TABLE IF NOT EXISTS product_reports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT NOT NULL,
  reporter_id INT NOT NULL,
  reason VARCHAR(255) NOT NULL,
  description TEXT,
  status ENUM('pending', 'reviewed', 'removed', 'false_report') DEFAULT 'pending',
  reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
  FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 6. Create `chats` Table
```sql
CREATE TABLE IF NOT EXISTS chats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT NOT NULL,
  buyer_id INT NOT NULL,
  seller_id INT NOT NULL,
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_message_date TIMESTAMP,
  FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
  FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY unique_chat (listing_id, buyer_id, seller_id)
);
```

### 7. Create `chat_messages` Table
```sql
CREATE TABLE IF NOT EXISTS chat_messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  chat_id INT NOT NULL,
  sender_id INT NOT NULL,
  message_text TEXT,
  sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_read BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
  FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## Phase 2: Backend Changes

### Key New Features:
1. **Single Registration**: One form for all users
2. **Free Trial Selling**: 5 days auto-expiration
3. **Smart Expiration**: Check if sold, if not offer boost
4. **Boost System**: Buy extended visibility
5. **Admin Analytics**: Revenue, growth, listings stats
6. **Review System**: Rate sellers after purchase
7. **Chat System**: Buyer-seller communication

---

## Phase 3: Frontend Changes

### Templates to Create/Update:
1. `register.html` - Single unified registration
2. `sell_product.html` - Simplified selling form (no package selection)
3. `product_detail.html` - Enhanced with boost options when expired
4. `admin_dashboard.html` - New analytics
5. `boost_purchase.html` - Boost package selection
6. `my_listings.html` - Show expiration dates, boost options
7. `chat.html` - Buyer-seller conversation

---

## Phase 4: Monetization Strategy

### Free Trial (5 days):
- All users get free 5-day listing
- Full visibility to buyers
- No charges if sold within 5 days

### After Expiration (If Not Sold):
Show boost options:
- **Basic Boost**: $5 for 7 days
- **Featured**: $10 for 14 days + homepage visibility
- **Premium Visibility**: $20 for 30 days + featured badge
- **Homepage Banner**: $50 for 30 days + banner placement

### Revenue Model:
- 100% free for first 3 listings per user
- After that: Pay only if you want boost/features
- No payment required to post

---

## Implementation Sequence

1. ✅ Create database migration script
2. Create new registration system (single form)
3. Update selling flow (remove package requirement)
4. Create expiration checker (cron job)
5. Create boost purchase system
6. Update admin dashboard
7. Create review/rating system
8. Create chat system (optional)
9. Testing and bug fixes

