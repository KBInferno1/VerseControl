-- PostgreSQL Initialization Script for LDS Hymnal Comparison Database
-- Database Schema: Traditional Christian Originals, 1985 LDS Hymnal, New Digital Hymns, and AI Change Logs

CREATE TABLE IF NOT EXISTS Hymns_Original (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    original_author VARCHAR(255),
    publication_year INT,
    original_source VARCHAR(255),
    lyrics TEXT NOT NULL,
    major_theme VARCHAR(100),
    minor_theme VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Hymns_1985 (
    id SERIAL PRIMARY KEY,
    hymn_number INT UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    lyrics TEXT NOT NULL,
    major_theme VARCHAR(100) CHECK (major_theme IN ('Taken from Christianity', 'LDS-specific', 'National/Patriotic', 'Other')),
    minor_theme VARCHAR(100),
    original_hymn_id INT REFERENCES Hymns_Original(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Hymns_New (
    id SERIAL PRIMARY KEY,
    hymn_number INT UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    lyrics TEXT NOT NULL,
    major_theme VARCHAR(100) CHECK (major_theme IN ('Taken from Christianity', 'LDS-specific', 'National/Patriotic', 'Other')),
    minor_theme VARCHAR(100),
    batch_release VARCHAR(50) DEFAULT 'Batch 1',
    hymn_1985_id INT REFERENCES Hymns_1985(id) ON DELETE SET NULL,
    original_hymn_id INT REFERENCES Hymns_Original(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Change_Logs (
    id SERIAL PRIMARY KEY,
    comparison_type VARCHAR(50) NOT NULL CHECK (comparison_type IN ('ORIGINAL_VS_1985', '1985_VS_NEW', 'ORIGINAL_VS_NEW', 'THREE_WAY')),
    original_hymn_id INT REFERENCES Hymns_Original(id) ON DELETE CASCADE,
    hymn_1985_id INT REFERENCES Hymns_1985(id) ON DELETE CASCADE,
    hymn_new_id INT REFERENCES Hymns_New(id) ON DELETE CASCADE,
    omitted_verses JSONB DEFAULT '[]'::jsonb,
    altered_phrases JSONB DEFAULT '[]'::jsonb,
    change_categories JSONB DEFAULT '[]'::jsonb,
    summary TEXT,
    major_theme VARCHAR(100),
    minor_theme VARCHAR(100),
    raw_ai_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_hymns_1985_number ON Hymns_1985(hymn_number);
CREATE INDEX IF NOT EXISTS idx_hymns_1985_themes ON Hymns_1985(major_theme, minor_theme);
CREATE INDEX IF NOT EXISTS idx_hymns_new_number ON Hymns_New(hymn_number);
CREATE INDEX IF NOT EXISTS idx_hymns_new_themes ON Hymns_New(major_theme, minor_theme);
CREATE INDEX IF NOT EXISTS idx_change_logs_type ON Change_Logs(comparison_type);
CREATE INDEX IF NOT EXISTS idx_change_logs_hymn_1985 ON Change_Logs(hymn_1985_id);
CREATE INDEX IF NOT EXISTS idx_change_logs_hymn_new ON Change_Logs(hymn_new_id);
CREATE INDEX IF NOT EXISTS idx_change_logs_original ON Change_Logs(original_hymn_id);
