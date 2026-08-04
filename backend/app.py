import os
import json
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

from ai_engine import analyze_hymn_comparison, HymnComparisonResult
from scraper import HymnScraper, get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LDS Hymnal Catalog & AI Comparison Engine API",
    description="Backend API for comparing 1985 LDS Hymnal, New Digital Hymns, and Traditional Christian Originals",
    version="1.0.0"
)

# Enable CORS for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompareRequest(BaseModel):
    hymn_1985_id: Optional[int] = None
    hymn_new_id: Optional[int] = None
    original_hymn_id: Optional[int] = None

def init_db_schema():
    logger.info("Verifying and initializing database tables...")
    statements = [
        """
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
        """,
        """
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
        """,
        """
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
        """,
        """
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
        """,
        "CREATE INDEX IF NOT EXISTS idx_hymns_1985_number ON Hymns_1985(hymn_number);",
        "CREATE INDEX IF NOT EXISTS idx_hymns_1985_themes ON Hymns_1985(major_theme, minor_theme);",
        "CREATE INDEX IF NOT EXISTS idx_hymns_new_number ON Hymns_New(hymn_number);",
        "CREATE INDEX IF NOT EXISTS idx_hymns_new_themes ON Hymns_New(major_theme, minor_theme);",
        "CREATE INDEX IF NOT EXISTS idx_change_logs_type ON Change_Logs(comparison_type);",
        "CREATE INDEX IF NOT EXISTS idx_change_logs_hymn_1985 ON Change_Logs(hymn_1985_id);",
        "CREATE INDEX IF NOT EXISTS idx_change_logs_hymn_new ON Change_Logs(hymn_new_id);",
        "CREATE INDEX IF NOT EXISTS idx_change_logs_original ON Change_Logs(original_hymn_id);",
        # Clean existing duplicates from prior runs
        "DELETE FROM Hymns_New a USING Hymns_New b WHERE a.id < b.id AND a.hymn_number = b.hymn_number;",
        "DELETE FROM Hymns_1985 a USING Hymns_1985 b WHERE a.id < b.id AND a.hymn_number = b.hymn_number;",
        "DELETE FROM Hymns_Original a USING Hymns_Original b WHERE a.id < b.id AND LOWER(a.title) = LOWER(b.title);",
        # Add UNIQUE constraints if missing
        "ALTER TABLE Hymns_New ADD CONSTRAINT hymns_new_number_unique UNIQUE (hymn_number);",
        "ALTER TABLE Hymns_Original ADD CONSTRAINT hymns_original_title_unique UNIQUE (title);",
        """
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
        """,
        """
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
        """,
        """
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
        """,
        """
        INSERT INTO Change_Logs (comparison_type, original_hymn_id, hymn_1985_id, hymn_new_id, omitted_verses, altered_phrases, change_categories, summary, major_theme, minor_theme, raw_ai_response)
        SELECT
            '1985_VS_NEW',
            horig.id,
            h1985.id,
            hnew.id,
            '["Verse 3 (1985 variation was omitted in favor of restoring Watts original Verse 3)"]'::jsonb,
            '[{"original": "Let men their songs employ", "new": "Let all their songs employ"}]'::jsonb,
            '["Inclusive language update", "Restoration of original Watts verse"]'::jsonb,
            'The change replaces gendered phrasing ("men") with inclusive phrasing ("all") and restores Isaac Watts'' original 3rd verse regarding grace overcoming the curse.',
            'Taken from Christianity',
            'Easter/Christmas',
            '{}'::jsonb
        FROM Hymns_1985 h1985
        JOIN Hymns_New hnew ON hnew.hymn_1985_id = h1985.id OR LOWER(hnew.title) = LOWER(h1985.title)
        LEFT JOIN Hymns_Original horig ON horig.id = h1985.original_hymn_id OR LOWER(horig.title) = LOWER(h1985.title)
        WHERE h1985.hymn_number = 201 OR LOWER(h1985.title) LIKE '%joy to the world%'
        LIMIT 1
        ON CONFLICT DO NOTHING;
        """
    ]

    try:
        conn = get_db_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            for stmt in statements:
                try:
                    cur.execute(stmt)
                except Exception as stmt_err:
                    logger.warning(f"Statement execution notice: {stmt_err}")
        conn.close()
        logger.info("Database tables verified/initialized successfully.")
    except Exception as e:
        logger.error(f"Error connecting for DB schema init: {e}")

# Helper to automatically run init_db_schema if any table missing
def ensure_db_initialized():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'hymns_1985';")
            res = cur.fetchone()
        conn.close()
        if not res:
            init_db_schema()
    except Exception:
        init_db_schema()

@app.on_event("startup")
def on_startup():
    init_db_schema()
    try:
        scraper = HymnScraper()
        scraper.seed_traditional_and_1985_hymns()
    except Exception as e:
        logger.error(f"Startup seed error: {e}")

@app.post("/api/seed/populate")
def populate_hymns_dataset(background_tasks: BackgroundTasks):
    def run_seed_task():
        scraper = HymnScraper()
        scraper.seed_traditional_and_1985_hymns()
        # Also poll and auto-link new digital hymns
        new_hymns = scraper.fetch_church_new_hymns_catalog()
        for item in new_hymns:
            scraper.save_new_hymn_to_db(item)

    background_tasks.add_task(run_seed_task)
    return {"message": "Hymnal population and auto-linking task dispatched in background."}

@app.post("/api/db/cleanup")
def cleanup_database():
    """
    Deduplicates records in Hymns_New, Hymns_1985, and Hymns_Original, and updates theme classifications.
    """
    conn = get_db_connection()
    conn.autocommit = True
    deleted_new = 0
    deleted_1985 = 0
    deleted_orig = 0
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Hymns_New a USING Hymns_New b WHERE a.id < b.id AND a.hymn_number = b.hymn_number;")
            deleted_new = cur.rowcount

            cur.execute("DELETE FROM Hymns_1985 a USING Hymns_1985 b WHERE a.id < b.id AND a.hymn_number = b.hymn_number;")
            deleted_1985 = cur.rowcount

            cur.execute("DELETE FROM Hymns_Original a USING Hymns_Original b WHERE a.id < b.id AND LOWER(a.title) = LOWER(b.title);")
            deleted_orig = cur.rowcount

            # Auto-align major_theme for hymns with Christian origins
            cur.execute("UPDATE Hymns_1985 SET major_theme = 'Taken from Christianity' WHERE original_hymn_id IS NOT NULL OR LOWER(title) IN (SELECT LOWER(title) FROM Hymns_Original);")
            cur.execute("UPDATE Hymns_1985 SET major_theme = 'LDS-specific' WHERE major_theme IS NULL AND original_hymn_id IS NULL;")
            cur.execute("UPDATE Hymns_New SET major_theme = 'Taken from Christianity' WHERE original_hymn_id IS NOT NULL OR LOWER(title) IN (SELECT LOWER(title) FROM Hymns_Original);")
            cur.execute("UPDATE Hymns_New SET major_theme = 'LDS-specific' WHERE major_theme IS NULL AND original_hymn_id IS NULL;")
        conn.close()
        return {
            "message": "Database cleanup and theme categorization completed.",
            "duplicates_removed": {
                "hymns_new": deleted_new,
                "hymns_1985": deleted_1985,
                "hymns_original": deleted_orig
            }
        }
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/summary")
def get_analytics_summary():
    """
    Returns aggregated taxonomy, change category, and historical timeline metrics for charts.
    """
    ensure_db_initialized()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Major Themes distribution (1985 Hymnal)
            cur.execute("""
                SELECT COALESCE(major_theme, 'Taken from Christianity') as name, COUNT(*) as value
                FROM Hymns_1985
                GROUP BY COALESCE(major_theme, 'Taken from Christianity')
                ORDER BY value DESC;
            """)
            major_themes = cur.fetchall()

            # 2. Minor Sub-Themes distribution
            cur.execute("""
                SELECT COALESCE(minor_theme, 'General Worship') as name, COUNT(*) as value
                FROM Hymns_1985
                WHERE minor_theme IS NOT NULL AND minor_theme <> ''
                GROUP BY COALESCE(minor_theme, 'General Worship')
                ORDER BY value DESC
                LIMIT 12;
            """)
            minor_themes = cur.fetchall()

            # 3. Change Categories frequency from Change_Logs
            cur.execute("""
                SELECT elem as name, COUNT(*) as value
                FROM Change_Logs, jsonb_array_elements_text(change_categories) as elem
                GROUP BY elem
                ORDER BY value DESC;
            """)
            change_categories = cur.fetchall()

            # 4. Historical Eras timeline from Hymns_Original
            cur.execute("""
                SELECT 
                    CASE 
                        WHEN publication_year < 1600 THEN '1500s (Reformation)'
                        WHEN publication_year BETWEEN 1600 AND 1699 THEN '1600s (Protestant)'
                        WHEN publication_year BETWEEN 1700 AND 1799 THEN '1700s (Watts & Wesley)'
                        WHEN publication_year BETWEEN 1800 AND 1899 THEN '1800s (Evangelical & Early LDS)'
                        WHEN publication_year >= 1900 THEN '1900s+ (Modern Print)'
                        ELSE 'Traditional (Pre-1800)'
                    END as era,
                    COUNT(*) as count
                FROM Hymns_Original
                WHERE publication_year IS NOT NULL
                GROUP BY era
                ORDER BY count DESC;
            """)
            timeline = cur.fetchall()

            # 5. Coverage stats
            cur.execute("SELECT COUNT(*) FROM Hymns_1985;")
            total_1985 = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(DISTINCT hymn_1985_id) FROM Change_Logs;")
            analyzed_1985 = cur.fetchone()["count"]

        conn.close()
        return {
            "major_themes": major_themes,
            "minor_themes": minor_themes,
            "change_categories": change_categories,
            "timeline": timeline,
            "coverage": {
                "total_hymns": total_1985,
                "analyzed_hymns": analyzed_1985,
                "percentage": round((analyzed_1985 / total_1985 * 100), 1) if total_1985 > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"Error fetching analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "lds-hymnal-compair-backend"}

@app.get("/api/stats")
def get_dashboard_stats():
    ensure_db_initialized()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM Hymns_Original;")
            count_original = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) FROM Hymns_1985;")
            count_1985 = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) FROM Hymns_New;")
            count_new = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) FROM Change_Logs;")
            count_logs = cur.fetchone()["count"]

            cur.execute("""
                SELECT major_theme, COUNT(*) as count 
                FROM Hymns_1985 
                WHERE major_theme IS NOT NULL 
                GROUP BY major_theme;
            """)
            theme_counts = cur.fetchall()

        return {
            "count_original": count_original,
            "count_1985": count_1985,
            "count_new": count_new,
            "count_change_logs": count_logs,
            "themes_breakdown": theme_counts
        }
    except Exception as e:
        logger.error(f"Stats query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/hymns/1985")
def get_1985_hymns(
    query: Optional[str] = None,
    major_theme: Optional[str] = None,
    limit: int = Query(500, ge=1, le=1000)
):
    ensure_db_initialized()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM Hymns_1985 WHERE 1=1"
            params = []
            if query:
                sql += " AND (title ILIKE %s OR lyrics ILIKE %s)"
                params.extend([f"%{query}%", f"%{query}%"])
            if major_theme == 'Taken from Christianity':
                sql += " AND (major_theme = %s OR original_hymn_id IS NOT NULL)"
                params.append(major_theme)
            elif major_theme:
                sql += " AND major_theme = %s"
                params.append(major_theme)
            sql += " ORDER BY hymn_number ASC LIMIT %s"
            params.append(limit)

            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()

@app.get("/api/hymns/new")
def get_new_hymns(
    query: Optional[str] = None,
    batch_release: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    ensure_db_initialized()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM Hymns_New WHERE 1=1"
            params = []
            if query:
                sql += " AND (title ILIKE %s OR lyrics ILIKE %s)"
                params.extend([f"%{query}%", f"%{query}%"])
            if batch_release:
                sql += " AND batch_release = %s"
                params.append(batch_release)
            sql += " ORDER BY hymn_number ASC LIMIT %s"
            params.append(limit)

            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()

@app.get("/api/hymns/lineage")
def get_hymn_lineage():
    """
    Returns 3-way mapped hymns: Original Christian Hymn ↔ 1985 LDS Hymnal ↔ New Digital Release.
    Uses subquery UNION ALL to combine 1985 hymns and brand-new digital hymns safely in Postgres.
    """
    ensure_db_initialized()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id_1985, number_1985, hymn_number_1985, title_1985, lyrics_1985, major_theme, minor_theme,
                    id_new, number_new, hymn_number_new, title_new, lyrics_new, batch_release,
                    id_original, title_original, original_author, publication_year, lyrics_original,
                    change_log_id, summary, omitted_verses, altered_phrases, change_categories
                FROM (
                    -- 1. All 1985 Hymns with linked New Release and Original Precursor (if any)
                    SELECT 
                        h1985.id as id_1985,
                        h1985.hymn_number as number_1985,
                        h1985.hymn_number as hymn_number_1985,
                        h1985.title as title_1985,
                        h1985.lyrics as lyrics_1985,
                        h1985.major_theme,
                        h1985.minor_theme,
                        hnew.id as id_new,
                        hnew.hymn_number as number_new,
                        hnew.hymn_number as hymn_number_new,
                        hnew.title as title_new,
                        hnew.lyrics as lyrics_new,
                        hnew.batch_release,
                        horig.id as id_original,
                        horig.title as title_original,
                        horig.original_author,
                        horig.publication_year,
                        horig.lyrics as lyrics_original,
                        cl.id as change_log_id,
                        cl.summary,
                        cl.omitted_verses,
                        cl.altered_phrases,
                        cl.change_categories,
                        COALESCE(h1985.hymn_number, hnew.hymn_number + 1000) as sort_order
                    FROM Hymns_1985 h1985
                    LEFT JOIN Hymns_New hnew ON hnew.hymn_1985_id = h1985.id OR LOWER(hnew.title) = LOWER(h1985.title)
                    LEFT JOIN Hymns_Original horig ON horig.id = h1985.original_hymn_id OR LOWER(horig.title) = LOWER(h1985.title)
                    LEFT JOIN Change_Logs cl ON cl.hymn_1985_id = h1985.id

                    UNION ALL

                    -- 2. Brand New Digital Release Hymns that have NO matching 1985 hymn
                    SELECT 
                        NULL as id_1985,
                        NULL as number_1985,
                        NULL as hymn_number_1985,
                        hnew.title as title_1985,
                        NULL as lyrics_1985,
                        hnew.major_theme,
                        hnew.minor_theme,
                        hnew.id as id_new,
                        hnew.hymn_number as number_new,
                        hnew.hymn_number as hymn_number_new,
                        hnew.title as title_new,
                        hnew.lyrics as lyrics_new,
                        hnew.batch_release,
                        horig.id as id_original,
                        horig.title as title_original,
                        horig.original_author,
                        horig.publication_year,
                        horig.lyrics as lyrics_original,
                        cl.id as change_log_id,
                        cl.summary,
                        cl.omitted_verses,
                        cl.altered_phrases,
                        cl.change_categories,
                        (hnew.hymn_number + 1000) as sort_order
                    FROM Hymns_New hnew
                    LEFT JOIN Hymns_1985 h1985 ON hnew.hymn_1985_id = h1985.id OR LOWER(hnew.title) = LOWER(h1985.title)
                    LEFT JOIN Hymns_Original horig ON horig.id = hnew.original_hymn_id OR LOWER(horig.title) = LOWER(hnew.title)
                    LEFT JOIN Change_Logs cl ON cl.hymn_new_id = hnew.id
                    WHERE h1985.id IS NULL
                ) lineage_sub
                ORDER BY sort_order ASC;
            """)
            return cur.fetchall()
    finally:
        conn.close()

@app.post("/api/compare/run")
def run_ai_comparison(req: CompareRequest):
    """
    Triggers Gemini LLM to compare available versions across 1985, New release, and Traditional Original precursor.
    Handles all 6 possible combinations of version availability.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            h1985 = None
            if req.hymn_1985_id:
                cur.execute("SELECT * FROM Hymns_1985 WHERE id = %s;", (req.hymn_1985_id,))
                h1985 = cur.fetchone()

            hnew = None
            if req.hymn_new_id:
                cur.execute("SELECT * FROM Hymns_New WHERE id = %s;", (req.hymn_new_id,))
                hnew = cur.fetchone()
            elif h1985:
                cur.execute("SELECT * FROM Hymns_New WHERE hymn_1985_id = %s OR LOWER(title) = LOWER(%s);", (h1985["id"], h1985["title"]))
                hnew = cur.fetchone()

            horig = None
            orig_id = req.original_hymn_id or (h1985.get("original_hymn_id") if h1985 else None) or (hnew.get("original_hymn_id") if hnew else None)
            if orig_id:
                cur.execute("SELECT * FROM Hymns_Original WHERE id = %s;", (orig_id,))
                horig = cur.fetchone()

            if not h1985 and not hnew and not horig:
                raise HTTPException(status_code=400, detail="At least one hymn entry (1985, New, or Original) must be specified for analysis.")

            lyrics_1985 = h1985["lyrics"] if h1985 else None
            lyrics_new = hnew["lyrics"] if hnew else None
            lyrics_orig = horig["lyrics"] if horig else None

            analysis_result = analyze_hymn_comparison(
                hymn_text_1985=lyrics_1985,
                hymn_text_new=lyrics_new,
                hymn_text_original=lyrics_orig
            )

            result_dict = analysis_result.model_dump()
            major = result_dict["classification"]["major_theme"]
            minor = result_dict["classification"]["minor_theme"]

            if h1985:
                cur.execute("UPDATE Hymns_1985 SET major_theme = %s, minor_theme = %s WHERE id = %s;", (major, minor, h1985["id"]))
            if hnew:
                cur.execute("UPDATE Hymns_New SET major_theme = %s, minor_theme = %s WHERE id = %s;", (major, minor, hnew["id"]))

            if h1985 and hnew and horig:
                comparison_type = "3_WAY"
            elif h1985 and hnew:
                comparison_type = "1985_VS_NEW"
            elif h1985 and horig:
                comparison_type = "1985_VS_ORIGINAL"
            elif hnew and horig:
                comparison_type = "NEW_VS_ORIGINAL"
            elif hnew:
                comparison_type = "NEW_ANALYSIS"
            else:
                comparison_type = "1985_ANALYSIS"

            if h1985:
                cur.execute("DELETE FROM Change_Logs WHERE hymn_1985_id = %s;", (h1985["id"],))
            elif hnew:
                cur.execute("DELETE FROM Change_Logs WHERE hymn_new_id = %s;", (hnew["id"],))

            cur.execute("""
                INSERT INTO Change_Logs (
                    comparison_type, original_hymn_id, hymn_1985_id, hymn_new_id,
                    omitted_verses, altered_phrases, change_categories, summary,
                    major_theme, minor_theme, raw_ai_response
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                comparison_type,
                horig["id"] if horig else None,
                h1985["id"] if h1985 else None,
                hnew["id"] if hnew else None,
                json.dumps(result_dict["omitted_verses"]),
                json.dumps(result_dict["altered_phrases"]),
                json.dumps(result_dict["change_categories"]),
                result_dict["summary"],
                major,
                minor,
                json.dumps(result_dict)
            ))
            conn.commit()

            return {
                "message": "AI Analysis completed successfully.",
                "analysis": result_dict
            }
    except Exception as e:
        conn.rollback()
        err_msg = str(e)
        logger.error(f"Error executing AI comparison: {e}")
        if "429" in err_msg or "rate limit" in err_msg.lower() or "RESOURCE_EXHAUSTED" in err_msg:
            raise HTTPException(status_code=429, detail="Gemini API rate limit reached (20 requests/minute free tier limit). Please wait ~30 seconds before clicking 'Run AI Theological Analysis' again.")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/scrape/trigger")
def trigger_scrape(background_tasks: BackgroundTasks):
    def run_scraper_task():
        scraper = HymnScraper()
        new_hymns = scraper.fetch_church_new_hymns_catalog()
        for item in new_hymns:
            scraper.save_new_hymn_to_db(item)

    background_tasks.add_task(run_scraper_task)
    return {"message": "Scraper job dispatched in background."}
