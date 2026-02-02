-- ===================================
-- REGEAR CATEGORY SYSTEM DATABASE SCHEMA
-- Complete hierarchical category management with filters
-- ===================================

-- ===================================
-- 1. MAIN CATEGORIES TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(20),
    display_order INT DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_slug (slug),
    INDEX idx_active (is_active),
    INDEX idx_order (display_order)
);

-- ===================================
-- 2. SUB-CATEGORIES TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS sub_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INT DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE KEY unique_category_slug (category_id, slug),
    INDEX idx_category (category_id),
    INDEX idx_active (is_active),
    INDEX idx_order (display_order)
);

-- ===================================
-- 3. FILTER TYPES TABLE
-- Defines available filter types (price, condition, brand, etc.)
-- ===================================
CREATE TABLE IF NOT EXISTS filter_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL, -- 'range', 'select', 'checkbox', 'multi_select', 'date'
    description TEXT,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_active (is_active)
);

-- ===================================
-- 4. CATEGORY FILTERS TABLE
-- Assigns filters to categories/sub-categories
-- ===================================
CREATE TABLE IF NOT EXISTS category_filters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    sub_category_id INT,
    filter_type_id INT NOT NULL,
    is_required TINYINT(1) DEFAULT 0,
    display_order INT DEFAULT 0,
    filter_config JSON,  -- Store filter-specific settings (min/max for range, options for select, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (sub_category_id) REFERENCES sub_categories(id) ON DELETE CASCADE,
    FOREIGN KEY (filter_type_id) REFERENCES filter_types(id) ON DELETE CASCADE,
    INDEX idx_category (category_id),
    INDEX idx_sub_category (sub_category_id),
    INDEX idx_order (display_order),
    CHECK (category_id IS NOT NULL OR sub_category_id IS NOT NULL)
);

-- ===================================
-- 5. FILTER OPTIONS TABLE
-- Predefined options for select/checkbox filters
-- ===================================
CREATE TABLE IF NOT EXISTS filter_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filter_type_id INT NOT NULL,
    option_value VARCHAR(100) NOT NULL,
    option_label VARCHAR(100) NOT NULL,
    display_order INT DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filter_type_id) REFERENCES filter_types(id) ON DELETE CASCADE,
    INDEX idx_filter_type (filter_type_id),
    UNIQUE KEY unique_filter_option (filter_type_id, option_value)
);

-- ===================================
-- 6. PRODUCT ATTRIBUTES TABLE
-- Stores product-specific attribute values (for filters)
-- ===================================
CREATE TABLE IF NOT EXISTS product_attributes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id INT NOT NULL,
    filter_type_id INT NOT NULL,
    attribute_value VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
    FOREIGN KEY (filter_type_id) REFERENCES filter_types(id) ON DELETE CASCADE,
    INDEX idx_listing (listing_id),
    INDEX idx_filter_type (filter_type_id),
    UNIQUE KEY unique_listing_filter (listing_id, filter_type_id)
);

-- ===================================
-- 7. INITIAL DATA POPULATION
-- ===================================

-- INSERT MAIN CATEGORIES
INSERT IGNORE INTO categories (name, slug, description, icon, color, display_order, is_active) VALUES
('Mobile Phones', 'mobile-phones', 'Smartphones and mobile devices', '📱', '#E91E63', 1, 1),
('Laptops & Computers', 'laptops-computers', 'Laptops, desktops, and computing devices', '💻', '#2196F3', 2, 1),
('Computer Components', 'computer-components', 'Hardware components and parts', '⚙️', '#FF9800', 3, 1),
('Storage Devices', 'storage-devices', 'Hard drives, SSDs, and storage solutions', '💾', '#9C27B0', 4, 1),
('Accessories', 'accessories', 'Cables, adapters, and accessories', '🔌', '#4CAF50', 5, 1),
('Gaming Equipment', 'gaming-equipment', 'Gaming consoles, controllers, and peripherals', '🎮', '#FF5722', 6, 1),
('Displays & Monitors', 'displays-monitors', 'Monitors and display screens', '🖥️', '#00BCD4', 7, 1),
('Office Electronics', 'office-electronics', 'Printers, scanners, and office equipment', '🖨️', '#607D8B', 8, 1),
('Cameras & Photography', 'cameras-photography', 'DSLR, mirrorless, and photography equipment', '📷', '#F44336', 9, 1),
('Networking Hardware', 'networking-hardware', 'Routers, modems, and networking equipment', '🌐', '#3F51B5', 10, 1);

-- ===================================
-- 8. INSERT SUB-CATEGORIES
-- ===================================

-- Mobile Phones Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'Apple iPhone', 'apple-iphone', 'iPhones of all models', 1, 1 FROM categories WHERE slug='mobile-phones'
UNION ALL
SELECT id, 'Samsung Galaxy', 'samsung-galaxy', 'Samsung Galaxy series', 2, 1 FROM categories WHERE slug='mobile-phones'
UNION ALL
SELECT id, 'OnePlus', 'oneplus', 'OnePlus devices', 3, 1 FROM categories WHERE slug='mobile-phones'
UNION ALL
SELECT id, 'Xiaomi & Poco', 'xiaomi-poco', 'Xiaomi and Poco phones', 4, 1 FROM categories WHERE slug='mobile-phones'
UNION ALL
SELECT id, 'Realme', 'realme', 'Realme devices', 5, 1 FROM categories WHERE slug='mobile-phones'
UNION ALL
SELECT id, 'Mobile Accessories', 'mobile-accessories', 'Phone cases, chargers, protectors', 6, 1 FROM categories WHERE slug='mobile-phones';

-- Laptops & Computers Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'Gaming Laptops', 'gaming-laptops', 'High-performance gaming laptops', 1, 1 FROM categories WHERE slug='laptops-computers'
UNION ALL
SELECT id, 'Business Laptops', 'business-laptops', 'Professional business laptops', 2, 1 FROM categories WHERE slug='laptops-computers'
UNION ALL
SELECT id, 'MacBooks', 'macbooks', 'Apple MacBook computers', 3, 1 FROM categories WHERE slug='laptops-computers'
UNION ALL
SELECT id, 'Desktop Computers', 'desktop-computers', 'Desktop PCs and workstations', 4, 1 FROM categories WHERE slug='laptops-computers'
UNION ALL
SELECT id, 'Ultrabooks', 'ultrabooks', 'Thin and light laptops', 5, 1 FROM categories WHERE slug='laptops-computers'
UNION ALL
SELECT id, 'Tablets', 'tablets', 'Tablets and iPad devices', 6, 1 FROM categories WHERE slug='laptops-computers';

-- Computer Components Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'Graphics Cards (GPU)', 'graphics-cards', 'Video cards and GPUs', 1, 1 FROM categories WHERE slug='computer-components'
UNION ALL
SELECT id, 'Processors (CPU)', 'processors', 'CPUs and processors', 2, 1 FROM categories WHERE slug='computer-components'
UNION ALL
SELECT id, 'Motherboards', 'motherboards', 'Computer motherboards', 3, 1 FROM categories WHERE slug='computer-components'
UNION ALL
SELECT id, 'RAM Memory', 'ram-memory', 'RAM and memory modules', 4, 1 FROM categories WHERE slug='computer-components'
UNION ALL
SELECT id, 'Power Supplies', 'power-supplies', 'PSU and power units', 5, 1 FROM categories WHERE slug='computer-components'
UNION ALL
SELECT id, 'Cooling Solutions', 'cooling-solutions', 'CPU coolers and fans', 6, 1 FROM categories WHERE slug='computer-components';

-- Storage Devices Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'Hard Disk Drives (HDD)', 'hard-disk-drives', '3.5\" and 2.5\" HDDs', 1, 1 FROM categories WHERE slug='storage-devices'
UNION ALL
SELECT id, 'Solid State Drives (SSD)', 'solid-state-drives', '2.5\" SATA SSDs', 2, 1 FROM categories WHERE slug='storage-devices'
UNION ALL
SELECT id, 'NVMe SSDs', 'nvme-ssd', 'M.2 NVMe drives', 3, 1 FROM categories WHERE slug='storage-devices'
UNION ALL
SELECT id, 'External Storage', 'external-storage', 'Portable and external drives', 4, 1 FROM categories WHERE slug='storage-devices'
UNION ALL
SELECT id, 'Memory Cards', 'memory-cards', 'SD, microSD, and memory cards', 5, 1 FROM categories WHERE slug='storage-devices'
UNION ALL
SELECT id, 'USB Flash Drives', 'usb-flash-drives', 'USB pen drives and sticks', 6, 1 FROM categories WHERE slug='storage-devices';

-- Accessories Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'Cables & Connectors', 'cables-connectors', 'USB, HDMI, and other cables', 1, 1 FROM categories WHERE slug='accessories'
UNION ALL
SELECT id, 'Adapters & Converters', 'adapters-converters', 'Power adapters and converters', 2, 1 FROM categories WHERE slug='accessories'
UNION ALL
SELECT id, 'Chargers', 'chargers', 'Charging devices and chargers', 3, 1 FROM categories WHERE slug='accessories'
UNION ALL
SELECT id, 'Power Banks', 'power-banks', 'Portable power banks', 4, 1 FROM categories WHERE slug='accessories'
UNION ALL
SELECT id, 'Docking Stations', 'docking-stations', 'Docking and charging stations', 5, 1 FROM categories WHERE slug='accessories';

-- Gaming Equipment Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'Gaming Consoles', 'gaming-consoles', 'PlayStation, Xbox, Nintendo', 1, 1 FROM categories WHERE slug='gaming-equipment'
UNION ALL
SELECT id, 'Gaming Controllers', 'gaming-controllers', 'Game controllers and joysticks', 2, 1 FROM categories WHERE slug='gaming-equipment'
UNION ALL
SELECT id, 'VR Headsets', 'vr-headsets', 'Virtual reality headsets', 3, 1 FROM categories WHERE slug='gaming-equipment'
UNION ALL
SELECT id, 'Gaming Chairs', 'gaming-chairs', 'Gaming and racing chairs', 4, 1 FROM categories WHERE slug='gaming-equipment'
UNION ALL
SELECT id, 'Gaming Accessories', 'gaming-accessories', 'Gaming mats, grips, and more', 5, 1 FROM categories WHERE slug='gaming-equipment';

-- Displays & Monitors Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, '24-27 inch Monitors', 'small-monitors', '24-27 inch display monitors', 1, 1 FROM categories WHERE slug='displays-monitors'
UNION ALL
SELECT id, '4K Monitors', '4k-monitors', '4K resolution monitors', 2, 1 FROM categories WHERE slug='displays-monitors'
UNION ALL
SELECT id, 'Gaming Monitors', 'gaming-monitors', 'High refresh rate gaming monitors', 3, 1 FROM categories WHERE slug='displays-monitors'
UNION ALL
SELECT id, 'Curved Monitors', 'curved-monitors', 'Curved display monitors', 4, 1 FROM categories WHERE slug='displays-monitors'
UNION ALL
SELECT id, 'Ultrawide Monitors', 'ultrawide-monitors', 'Ultrawide and super-wide monitors', 5, 1 FROM categories WHERE slug='displays-monitors'
UNION ALL
SELECT id, 'Projectors', 'projectors', 'Home and professional projectors', 6, 1 FROM categories WHERE slug='displays-monitors';

-- Office Electronics Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'Printers', 'printers', 'Inkjet and laser printers', 1, 1 FROM categories WHERE slug='office-electronics'
UNION ALL
SELECT id, 'Scanners', 'scanners', 'Document and flatbed scanners', 2, 1 FROM categories WHERE slug='office-electronics'
UNION ALL
SELECT id, 'Multifunction Devices', 'multifunction-devices', 'All-in-one printer/scanner devices', 3, 1 FROM categories WHERE slug='office-electronics'
UNION ALL
SELECT id, 'Shredders', 'shredders', 'Paper shredders', 4, 1 FROM categories WHERE slug='office-electronics'
UNION ALL
SELECT id, 'Laminating Machines', 'laminating-machines', 'Document laminating machines', 5, 1 FROM categories WHERE slug='office-electronics';

-- Cameras & Photography Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'DSLR Cameras', 'dslr-cameras', 'Digital SLR cameras', 1, 1 FROM categories WHERE slug='cameras-photography'
UNION ALL
SELECT id, 'Mirrorless Cameras', 'mirrorless-cameras', 'Mirrorless digital cameras', 2, 1 FROM categories WHERE slug='cameras-photography'
UNION ALL
SELECT id, 'Camera Lenses', 'camera-lenses', 'Interchangeable lenses', 3, 1 FROM categories WHERE slug='cameras-photography'
UNION ALL
SELECT id, 'Action Cameras', 'action-cameras', 'GoPro and action cameras', 4, 1 FROM categories WHERE slug='cameras-photography'
UNION ALL
SELECT id, 'Photography Lighting', 'photography-lighting', 'Studio lights and reflectors', 5, 1 FROM categories WHERE slug='cameras-photography'
UNION ALL
SELECT id, 'Camera Tripods', 'camera-tripods', 'Tripods and monopods', 6, 1 FROM categories WHERE slug='cameras-photography';

-- Networking Hardware Sub-Categories
INSERT IGNORE INTO sub_categories (category_id, name, slug, description, display_order, is_active) 
SELECT id, 'WiFi Routers', 'wifi-routers', 'WiFi and mesh routers', 1, 1 FROM categories WHERE slug='networking-hardware'
UNION ALL
SELECT id, 'Modems', 'modems', 'Network modems and gateways', 2, 1 FROM categories WHERE slug='networking-hardware'
UNION ALL
SELECT id, 'Network Switches', 'network-switches', 'Ethernet switches', 3, 1 FROM categories WHERE slug='networking-hardware'
UNION ALL
SELECT id, 'WiFi Extenders', 'wifi-extenders', 'WiFi range extenders', 4, 1 FROM categories WHERE slug='networking-hardware'
UNION ALL
SELECT id, 'Network Cables', 'network-cables', 'Ethernet and network cables', 5, 1 FROM categories WHERE slug='networking-hardware';

-- ===================================
-- 9. INSERT FILTER TYPES
-- ===================================

INSERT IGNORE INTO filter_types (name, slug, type, description, is_active) VALUES
('Price Range', 'price-range', 'range', 'Filter by price (min - max)', 1),
('Condition', 'condition', 'multi_select', 'New, Like New, Used, For Parts', 1),
('Brand', 'brand', 'multi_select', 'Product brand/manufacturer', 1),
('Location', 'location', 'select', 'City or state location', 1),
('Posted Date', 'posted-date', 'select', 'When listing was posted', 1),
('Processor (CPU)', 'processor', 'multi_select', 'CPU type for computers', 1),
('RAM', 'ram', 'multi_select', 'RAM capacity in GB', 1),
('Storage Type', 'storage-type', 'multi_select', 'HDD, SSD, NVMe', 1),
('Screen Size', 'screen-size', 'multi_select', 'Display size in inches', 1),
('Mobile Brand', 'mobile-brand', 'multi_select', 'Mobile phone brand', 1),
('Storage Capacity', 'storage-capacity', 'multi_select', 'Storage in GB/TB', 1),
('Warranty Status', 'warranty-status', 'multi_select', 'With/Without warranty', 1),
('Graphics Card', 'graphics-card', 'multi_select', 'GPU/Video card model', 1),
('Resolution', 'resolution', 'multi_select', 'Screen resolution (1080p, 4K, etc)', 1),
('Refresh Rate', 'refresh-rate', 'multi_select', 'Monitor refresh rate (Hz)', 1);

-- ===================================
-- 10. ASSIGN FILTERS TO CATEGORIES
-- ===================================

-- Common filters for all categories (price, condition, brand, location, posted date)
INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, CASE WHEN ft.slug IN ('price-range', 'condition') THEN 1 ELSE 0 END, 
CASE WHEN ft.slug = 'price-range' THEN 1 WHEN ft.slug = 'condition' THEN 2 WHEN ft.slug = 'brand' THEN 3 WHEN ft.slug = 'location' THEN 4 WHEN ft.slug = 'posted-date' THEN 5 ELSE 6 END,
JSON_OBJECT('placeholder', 'Enter value')
FROM categories c
CROSS JOIN filter_types ft
WHERE ft.slug IN ('price-range', 'condition', 'brand', 'location', 'posted-date');

-- Mobile Phones specific filters
INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, 0, 6, JSON_OBJECT('placeholder', 'Select storage')
FROM categories c
JOIN filter_types ft ON ft.slug = 'storage-capacity'
WHERE c.slug = 'mobile-phones';

INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, 0, 7, JSON_OBJECT('placeholder', 'Select RAM')
FROM categories c
JOIN filter_types ft ON ft.slug = 'ram'
WHERE c.slug = 'mobile-phones';

-- Laptops & Computers specific filters
INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, 0, 6, JSON_OBJECT('placeholder', 'Select processor')
FROM categories c
JOIN filter_types ft ON ft.slug = 'processor'
WHERE c.slug = 'laptops-computers';

INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, 0, 7, JSON_OBJECT('placeholder', 'Select RAM')
FROM categories c
JOIN filter_types ft ON ft.slug = 'ram'
WHERE c.slug = 'laptops-computers';

INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, 0, 8, JSON_OBJECT('placeholder', 'Select storage type')
FROM categories c
JOIN filter_types ft ON ft.slug = 'storage-type'
WHERE c.slug = 'laptops-computers';

INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, 0, 9, JSON_OBJECT('placeholder', 'Select screen size')
FROM categories c
JOIN filter_types ft ON ft.slug = 'screen-size'
WHERE c.slug = 'laptops-computers';

-- Displays & Monitors specific filters
INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, 0, 6, JSON_OBJECT('placeholder', 'Select resolution')
FROM categories c
JOIN filter_types ft ON ft.slug = 'resolution'
WHERE c.slug = 'displays-monitors';

INSERT IGNORE INTO category_filters (category_id, filter_type_id, is_required, display_order, filter_config)
SELECT c.id, ft.id, 0, 7, JSON_OBJECT('placeholder', 'Select refresh rate')
FROM categories c
JOIN filter_types ft ON ft.slug = 'refresh-rate'
WHERE c.slug = 'displays-monitors';

-- ===================================
-- 11. INSERT FILTER OPTIONS
-- ===================================

-- Condition options
INSERT IGNORE INTO filter_options (filter_type_id, option_value, option_label, display_order, is_active)
SELECT id, 'new', 'New', 1, 1 FROM filter_types WHERE slug = 'condition'
UNION ALL
SELECT id, 'like-new', 'Like New', 2, 1 FROM filter_types WHERE slug = 'condition'
UNION ALL
SELECT id, 'used', 'Used', 3, 1 FROM filter_types WHERE slug = 'condition'
UNION ALL
SELECT id, 'for-parts', 'For Parts', 4, 1 FROM filter_types WHERE slug = 'condition';

-- Posted Date options
INSERT IGNORE INTO filter_options (filter_type_id, option_value, option_label, display_order, is_active)
SELECT id, 'last-24h', 'Last 24 Hours', 1, 1 FROM filter_types WHERE slug = 'posted-date'
UNION ALL
SELECT id, 'last-7d', 'Last 7 Days', 2, 1 FROM filter_types WHERE slug = 'posted-date'
UNION ALL
SELECT id, 'last-30d', 'Last 30 Days', 3, 1 FROM filter_types WHERE slug = 'posted-date'
UNION ALL
SELECT id, 'any-time', 'Any Time', 4, 1 FROM filter_types WHERE slug = 'posted-date';

-- RAM Options
INSERT IGNORE INTO filter_options (filter_type_id, option_value, option_label, display_order, is_active)
SELECT id, '4gb', '4 GB', 1, 1 FROM filter_types WHERE slug = 'ram'
UNION ALL
SELECT id, '8gb', '8 GB', 2, 1 FROM filter_types WHERE slug = 'ram'
UNION ALL
SELECT id, '16gb', '16 GB', 3, 1 FROM filter_types WHERE slug = 'ram'
UNION ALL
SELECT id, '32gb', '32 GB', 4, 1 FROM filter_types WHERE slug = 'ram'
UNION ALL
SELECT id, '64gb', '64 GB', 5, 1 FROM filter_types WHERE slug = 'ram';

-- Storage Capacity Options (for phones/tablets)
INSERT IGNORE INTO filter_options (filter_type_id, option_value, option_label, display_order, is_active)
SELECT id, '32gb', '32 GB', 1, 1 FROM filter_types WHERE slug = 'storage-capacity'
UNION ALL
SELECT id, '64gb', '64 GB', 2, 1 FROM filter_types WHERE slug = 'storage-capacity'
UNION ALL
SELECT id, '128gb', '128 GB', 3, 1 FROM filter_types WHERE slug = 'storage-capacity'
UNION ALL
SELECT id, '256gb', '256 GB', 4, 1 FROM filter_types WHERE slug = 'storage-capacity'
UNION ALL
SELECT id, '512gb', '512 GB', 5, 1 FROM filter_types WHERE slug = 'storage-capacity'
UNION ALL
SELECT id, '1tb', '1 TB', 6, 1 FROM filter_types WHERE slug = 'storage-capacity';

-- Storage Type Options
INSERT IGNORE INTO filter_options (filter_type_id, option_value, option_label, display_order, is_active)
SELECT id, 'hdd', 'HDD', 1, 1 FROM filter_types WHERE slug = 'storage-type'
UNION ALL
SELECT id, 'ssd', 'SSD (SATA)', 2, 1 FROM filter_types WHERE slug = 'storage-type'
UNION ALL
SELECT id, 'nvme', 'NVMe SSD', 3, 1 FROM filter_types WHERE slug = 'storage-type'
UNION ALL
SELECT id, 'hybrid', 'Hybrid', 4, 1 FROM filter_types WHERE slug = 'storage-type';

-- Screen Size Options
INSERT IGNORE INTO filter_options (filter_type_id, option_value, option_label, display_order, is_active)
SELECT id, '13inch', '13"', 1, 1 FROM filter_types WHERE slug = 'screen-size'
UNION ALL
SELECT id, '14inch', '14"', 2, 1 FROM filter_types WHERE slug = 'screen-size'
UNION ALL
SELECT id, '15inch', '15"', 3, 1 FROM filter_types WHERE slug = 'screen-size'
UNION ALL
SELECT id, '16inch', '16"', 4, 1 FROM filter_types WHERE slug = 'screen-size'
UNION ALL
SELECT id, '17inch', '17"', 5, 1 FROM filter_types WHERE slug = 'screen-size';

-- Resolution Options
INSERT IGNORE INTO filter_options (filter_type_id, option_value, option_label, display_order, is_active)
SELECT id, '1080p', 'Full HD (1080p)', 1, 1 FROM filter_types WHERE slug = 'resolution'
UNION ALL
SELECT id, '1440p', 'QHD (1440p)', 2, 1 FROM filter_types WHERE slug = 'resolution'
UNION ALL
SELECT id, '4k', '4K (2160p)', 3, 1 FROM filter_types WHERE slug = 'resolution'
UNION ALL
SELECT id, '5k', '5K', 4, 1 FROM filter_types WHERE slug = 'resolution';

-- Refresh Rate Options
INSERT IGNORE INTO filter_options (filter_type_id, option_value, option_label, display_order, is_active)
SELECT id, '60hz', '60 Hz', 1, 1 FROM filter_types WHERE slug = 'refresh-rate'
UNION ALL
SELECT id, '75hz', '75 Hz', 2, 1 FROM filter_types WHERE slug = 'refresh-rate'
UNION ALL
SELECT id, '120hz', '120 Hz', 3, 1 FROM filter_types WHERE slug = 'refresh-rate'
UNION ALL
SELECT id, '144hz', '144 Hz', 4, 1 FROM filter_types WHERE slug = 'refresh-rate'
UNION ALL
SELECT id, '165hz', '165 Hz', 5, 1 FROM filter_types WHERE slug = 'refresh-rate'
UNION ALL
SELECT id, '240hz', '240 Hz', 6, 1 FROM filter_types WHERE slug = 'refresh-rate';

-- ===================================
-- 12. UPDATE LISTINGS TABLE FOR CATEGORIES
-- ===================================

ALTER TABLE listings ADD COLUMN IF NOT EXISTS category_id INT;
ALTER TABLE listings ADD COLUMN IF NOT EXISTS sub_category_id INT;
ALTER TABLE listings ADD FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL;
ALTER TABLE listings ADD FOREIGN KEY (sub_category_id) REFERENCES sub_categories(id) ON DELETE SET NULL;

-- ===================================
-- DONE: Complete category system with dynamic filters
-- ===================================
