-- PostgreSQL Initialization Script for LDS Hymnal Comparison Database
-- Database Schema: Traditional Christian Originals, 1985 LDS Hymnal, New Digital Hymns, and AI Change Logs

CREATE TABLE IF NOT EXISTS Hymns_Original (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
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
    hymn_number INT NOT NULL,
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

-- Sample Seed Data for immediate testing and verification
INSERT INTO Hymns_Original (title, original_author, publication_year, original_source, lyrics, major_theme, minor_theme)
VALUES (
    'Joy to the World',
    'Isaac Watts',
    1719,
    'Psalms of David Imitated in the Language of the New Testament',
    'Verse 1: Joy to the world, the Lord is come! Let earth receive her King; Let ev''ry heart prepare him room, And heav''n and nature sing.' || E'\n' ||
    'Verse 2: Joy to the earth, the Savior reigns! Let men their songs employ; While fields and floods, rocks, hills, and plains Repeat the sounding joy.' || E'\n' ||
    'Verse 3: No more let sins and sorrows grow, Nor thorns infest the ground; He comes to make his blessings flow Far as the curse is found.' || E'\n' ||
    'Verse 4: He rules the world with truth and grace, And makes the nations prove The glories of his righteousness, And wonders of his love.',
    'Taken from Christianity',
    'Easter/Christmas'
) ON CONFLICT DO NOTHING;

INSERT INTO Hymns_1985 (hymn_number, title, lyrics, major_theme, minor_theme, original_hymn_id)
VALUES (
    201,
    'Joy to the World',
    'Verse 1: Joy to the world, the Lord is come! Let earth receive her King; Let ev''ry heart prepare him room, And heav''n and nature sing, And heav''n and nature sing, And heav''n, and heav''n and nature sing.' || E'\n' ||
    'Verse 2: Joy to the earth, the Savior reigns! Let men their songs employ; While fields and floods, rocks, hills, and plains Repeat the sounding joy, Repeat the sounding joy, Repeat, repeat the sounding joy.' || E'\n' ||
    'Verse 3: Rejoice! Rejoice when Jesus reigns, And saints their songs employ; While fields and floods, rocks, hills, and plains Repeat the sounding joy.' || E'\n' ||
    'Verse 4: He rules the world with truth and grace, And makes the nations prove The glories of his righteousness, And wonders of his love, And wonders of his love, And wonders, wonders of his love.',
    'Taken from Christianity',
    'Easter/Christmas',
    1
) ON CONFLICT (hymn_number) DO NOTHING;

INSERT INTO Hymns_New (hymn_number, title, lyrics, major_theme, minor_theme, batch_release, hymn_1985_id, original_hymn_id)
VALUES (
    1001,
    'Joy to the World',
    'Verse 1: Joy to the world, the Lord is come! Let earth receive her King; Let ev''ry heart prepare him room, And heav''n and nature sing.' || E'\n' ||
    'Verse 2: Joy to the earth, the Savior reigns! Let all their songs employ; While fields and floods, rocks, hills, and plains Repeat the sounding joy.' || E'\n' ||
    'Verse 3: No more let sins and sorrows grow, Nor thorns infest the ground; He comes to make his blessings flow Far as the curse is found.' || E'\n' ||
    'Verse 4: He rules the world with truth and grace, And makes the nations prove The glories of his righteousness, And wonders of his love.',
    'Taken from Christianity',
    'Easter/Christmas',
    'Batch 1',
    1,
    1
) ON CONFLICT DO NOTHING;

INSERT INTO Change_Logs (comparison_type, original_hymn_id, hymn_1985_id, hymn_new_id, omitted_verses, altered_phrases, change_categories, summary, major_theme, minor_theme, raw_ai_response)
VALUES (
    '1985_VS_NEW',
    1,
    1,
    1,
    '["Verse 3 (1985 variation was omitted in favor of restoring Watts original Verse 3)"]'::jsonb,
    '[{"original": "Let men their songs employ", "new": "Let all their songs employ"}]'::jsonb,
    '["Inclusive language update", "Restoration of original Watts verse"]'::jsonb,
    'The change replaces gendered phrasing ("men") with inclusive phrasing ("all") and restores Isaac Watts'' original 3rd verse regarding grace overcoming the curse.',
    'Taken from Christianity',
    'Easter/Christmas',
    '{}'::jsonb
) ON CONFLICT DO NOTHING;
