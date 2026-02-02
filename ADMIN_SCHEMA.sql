-- ===================================
-- ADMIN DASHBOARD DATABASE SCHEMA
-- ===================================

-- Admin logs table (activity tracking)
CREATE TABLE IF NOT EXISTS admin_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action VARCHAR(255),
    description TEXT,
    table_affected VARCHAR(100),
    record_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id)
);

-- Complaints/Reports table
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reporter_id INT NOT NULL,
    reported_user_id INT,
    listing_id INT,
    complaint_type VARCHAR(100), -- 'fake_product', 'inappropriate', 'scam', 'poor_condition', 'other'
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'investigating', 'resolved', 'dismissed'
    admin_action VARCHAR(255),
    admin_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (reporter_id) REFERENCES users(id),
    FOREIGN KEY (reported_user_id) REFERENCES users(id),
    FOREIGN KEY (listing_id) REFERENCES listings(id),
    FOREIGN KEY (admin_id) REFERENCES users(id)
);

-- Update listings table to add approval status
ALTER TABLE listings ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending' COMMENT 'pending, approved, rejected, sold';
ALTER TABLE listings ADD COLUMN IF NOT EXISTS admin_notes TEXT;
ALTER TABLE listings ADD COLUMN IF NOT EXISTS approved_by INT;
ALTER TABLE listings ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP NULL;

-- Activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    activity_type VARCHAR(100), -- 'login', 'logout', 'post_listing', 'update_listing', 'view_listing', 'contact_seller'
    description TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Admin announcements/notifications
CREATE TABLE IF NOT EXISTS admin_announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    title VARCHAR(255),
    message TEXT,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id)
);

-- Add approval-related columns to users if not exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS warning_count INT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_warning_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS suspension_reason TEXT;

-- Create index for faster queries
CREATE INDEX idx_listings_approval_status ON listings(approval_status);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_admin_logs_admin ON admin_logs(admin_id);
