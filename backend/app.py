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
    hymn_1985_id: int
    hymn_new_id: Optional[int] = None
    original_hymn_id: Optional[int] = None

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "lds-hymnal-compair-backend"}

@app.get("/api/stats")
def get_dashboard_stats():
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
    limit: int = Query(100, ge=1, le=500)
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM Hymns_1985 WHERE 1=1"
            params = []
            if query:
                sql += " AND (title ILIKE %s OR lyrics ILIKE %s)"
                params.extend([f"%{query}%", f"%{query}%"])
            if major_theme:
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
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    h1985.id as id_1985,
                    h1985.hymn_number as number_1985,
                    h1985.title as title_1985,
                    h1985.lyrics as lyrics_1985,
                    h1985.major_theme,
                    h1985.minor_theme,
                    hnew.id as id_new,
                    hnew.hymn_number as number_new,
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
                    cl.change_categories
                FROM Hymns_1985 h1985
                LEFT JOIN Hymns_New hnew ON hnew.hymn_1985_id = h1985.id OR LOWER(hnew.title) = LOWER(h1985.title)
                LEFT JOIN Hymns_Original horig ON h1985.original_hymn_id = horig.id OR hnew.original_hymn_id = horig.id
                LEFT JOIN Change_Logs cl ON cl.hymn_1985_id = h1985.id
                ORDER BY h1985.hymn_number ASC;
            """)
            return cur.fetchall()
    finally:
        conn.close()

@app.post("/api/compare/run")
def run_ai_comparison(req: CompareRequest):
    """
    Triggers Gemini LLM to compare 1985 vs New (and Original if linked), and saves structured JSON result into Change_Logs.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Fetch 1985 hymn
            cur.execute("SELECT * FROM Hymns_1985 WHERE id = %s;", (req.hymn_1985_id,))
            h1985 = cur.fetchone()
            if not h1985:
                raise HTTPException(status_code=404, detail="1985 Hymn not found")

            # Fetch New hymn
            hnew = None
            if req.hymn_new_id:
                cur.execute("SELECT * FROM Hymns_New WHERE id = %s;", (req.hymn_new_id,))
                hnew = cur.fetchone()
            else:
                cur.execute("SELECT * FROM Hymns_New WHERE hymn_1985_id = %s OR LOWER(title) = LOWER(%s);", (req.hymn_1985_id, h1985["title"]))
                hnew = cur.fetchone()

            # Fetch Original hymn if exists
            horig = None
            orig_id = req.original_hymn_id or h1985.get("original_hymn_id")
            if orig_id:
                cur.execute("SELECT * FROM Hymns_Original WHERE id = %s;", (orig_id,))
                horig = cur.fetchone()

            if not hnew:
                raise HTTPException(status_code=400, detail="Matching New Hymnal release not found for comparison.")

            # Run AI Engine
            lyrics_1985 = h1985["lyrics"]
            lyrics_new = hnew["lyrics"]
            lyrics_orig = horig["lyrics"] if horig else None

            analysis_result = analyze_hymn_comparison(
                hymn_text_1985=lyrics_1985,
                hymn_text_new=lyrics_new,
                hymn_text_original=lyrics_orig
            )

            # Convert result to dict
            result_dict = analysis_result.model_dump()

            # Update DB themes
            cur.execute("""
                UPDATE Hymns_1985 
                SET major_theme = %s, minor_theme = %s 
                WHERE id = %s;
            """, (result_dict["classification"]["major_theme"], result_dict["classification"]["minor_theme"], h1985["id"]))

            cur.execute("""
                UPDATE Hymns_New 
                SET major_theme = %s, minor_theme = %s 
                WHERE id = %s;
            """, (result_dict["classification"]["major_theme"], result_dict["classification"]["minor_theme"], hnew["id"]))

            # Save to Change_Logs
            cur.execute("""
                INSERT INTO Change_Logs (
                    comparison_type, original_hymn_id, hymn_1985_id, hymn_new_id,
                    omitted_verses, altered_phrases, change_categories, summary,
                    major_theme, minor_theme, raw_ai_response
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                "1985_VS_NEW",
                horig["id"] if horig else None,
                h1985["id"],
                hnew["id"],
                json.dumps(result_dict["omitted_verses"]),
                json.dumps(result_dict["altered_phrases"]),
                json.dumps(result_dict["change_categories"]),
                result_dict["summary"],
                result_dict["classification"]["major_theme"],
                result_dict["classification"]["minor_theme"],
                json.dumps(result_dict)
            ))
            conn.commit()

            return {
                "message": "AI Comparison completed successfully.",
                "analysis": result_dict
            }
    except Exception as e:
        conn.rollback()
        logger.error(f"Error executing AI comparison: {e}")
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
