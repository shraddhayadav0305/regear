-- ReGear Admin Dashboard Database Schema
-- Run this to set up admin functionality

-- Create admin_logs table
CREATE TABLE IF NOT EXISTS admin_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action VARCHAR(255),
    description TEXT,
    table_affected VARCHAR(100),
    record_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_admin_id (admin_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create complaints table
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reporter_id INT,
    reported_user_id INT,
    listing_id INT,
    complaint_type VARCHAR(100),
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    admin_action TEXT,
    admin_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (reported_user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE SET NULL,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_reported_user (reported_user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create activity_logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(100),
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_activity_type (activity_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create admin_announcements table
CREATE TABLE IF NOT EXISTS admin_announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT,
    title VARCHAR(255),
    message TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Extend listings table with approval fields
ALTER TABLE listings ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending' COMMENT 'pending, approved, rejected, sold';
ALTER TABLE listings ADD COLUMN IF NOT EXISTS admin_notes TEXT;
ALTER TABLE listings ADD COLUMN IF NOT EXISTS approved_by INT;
ALTER TABLE listings ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP NULL;

-- Extend users table with warning fields
ALTER TABLE users ADD COLUMN IF NOT EXISTS warning_count INT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_warning_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS suspension_reason TEXT;

-- Add indexes for listings
ALTER TABLE listings ADD INDEX IF NOT EXISTS idx_approval_status (approval_status);
ALTER TABLE listings ADD INDEX IF NOT EXISTS idx_approved_at (approved_at);

-- All done
