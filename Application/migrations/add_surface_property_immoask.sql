-- Migration: ajout surface_m2, property_type et table immoask_announcements

-- real_estate_announcements
ALTER TABLE real_estate_announcements ADD COLUMN IF NOT EXISTS surface_m2 FLOAT NULL;
ALTER TABLE real_estate_announcements ADD COLUMN IF NOT EXISTS property_type VARCHAR(100) NULL;

-- coinafrique_announcements
ALTER TABLE coinafrique_announcements ADD COLUMN surface_m2 FLOAT NULL;
ALTER TABLE coinafrique_announcements ADD COLUMN property_type VARCHAR(100) NULL;

-- igoe_announcements
ALTER TABLE igoe_announcements ADD COLUMN surface_m2 FLOAT NULL;
ALTER TABLE igoe_announcements ADD COLUMN property_type VARCHAR(100) NULL;

-- intendance_announcements
ALTER TABLE intendance_announcements ADD COLUMN surface_m2 FLOAT NULL;
ALTER TABLE intendance_announcements ADD COLUMN property_type VARCHAR(100) NULL;

-- Table immoask_announcements
CREATE TABLE IF NOT EXISTS immoask_announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    external_id VARCHAR(255) NOT NULL UNIQUE,
    source VARCHAR(100) NOT NULL DEFAULT 'Immoask',
    price VARCHAR(100) NULL,
    price_numeric FLOAT NULL,
    location VARCHAR(255) NULL,
    description TEXT NULL,
    surface_m2 FLOAT NULL,
    property_type VARCHAR(100) NULL,
    images JSON NULL,
    source_url VARCHAR(500) NULL,
    citations JSON NULL,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_external_id (external_id),
    INDEX idx_location (location),
    INDEX idx_surface (surface_m2)
);
