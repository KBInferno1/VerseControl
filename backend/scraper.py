import os
import re
import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHURCH_MUSIC_LIBRARY_URL = "https://www.churchofjesuschrist.org/study/music/hymns-for-home-and-church"

def get_db_connection():
    db_host = os.getenv("POSTGRES_HOST", "db")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "hymnal_db")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_pass = os.getenv("POSTGRES_PASSWORD", "postgres")

    return psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_pass,
        cursor_factory=RealDictCursor
    )

class HymnScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def fetch_church_new_hymns_catalog(self) -> List[Dict[str, Any]]:
        """
        Polls the Church digital music library for newly released hymns in 'Hymns—for Home and Church'.
        """
        logger.info(f"Polling Church Music Library at {CHURCH_MUSIC_LIBRARY_URL}...")
        try:
            with httpx.Client(timeout=15.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
                response = client.get(CHURCH_MUSIC_LIBRARY_URL)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            hymns_found = []

            # Search for hymn links / cards in the DOM structure
            links = soup.find_all("a", href=re.compile(r"/study/music/hymns-for-home-and-church/"))
            for link in links:
                title_text = link.get_text(strip=True)
                href = link.get("href", "")
                if title_text and href:
                    # Parse hymn number if present in text
                    match = re.search(r"^(\d+)\.\s*(.*)", title_text)
                    if match:
                        num = int(match.group(1))
                        title = match.group(2)
                    else:
                        num = 1000 + len(hymns_found) + 1
                        title = title_text

                    hymns_found.append({
                        "hymn_number": num,
                        "title": title,
                        "url": f"https://www.churchofjesuschrist.org{href}" if href.startswith("/") else href,
                        "batch_release": "Batch 1"
                    })

            logger.info(f"Found {len(hymns_found)} hymns in Church digital library.")
            return hymns_found
        except Exception as e:
            logger.error(f"Error scraping Church music library: {e}")
            return []

    def fetch_hymn_lyrics_from_url(self, url: str) -> str:
        """
        Fetches lyrics content from a specific Church study URL.
        """
        try:
            with httpx.Client(timeout=10.0, headers=self.headers) as client:
                resp = client.get(url)
                resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Look for verse body containers
            verses = soup.find_all(["div", "p"], class_=re.compile(r"verse|stanza|body"))
            if verses:
                return "\n".join([v.get_text(separator=" ", strip=True) for v in verses])
            
            # Fallback text extraction
            main_body = soup.find("main") or soup.find("article")
            if main_body:
                return main_body.get_text(separator="\n", strip=True)
            
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Failed to fetch lyrics from {url}: {e}")
            return ""

    def save_new_hymn_to_db(self, hymn_data: Dict[str, Any]) -> Optional[int]:
        """
        Saves or updates a new hymn entry in PostgreSQL.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Hymns_New (hymn_number, title, lyrics, batch_release)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id;
                """, (
                    hymn_data["hymn_number"],
                    hymn_data["title"],
                    hymn_data.get("lyrics", "Lyrics pending ingestion..."),
                    hymn_data.get("batch_release", "Batch 1")
                ))
                res = cur.fetchone()
                conn.commit()
                return res["id"] if res else None
        except Exception as e:
            logger.error(f"Database insertion error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

if __name__ == "__main__":
    scraper = HymnScraper()
    print("Testing HymnScraper instance...")
    catalog = scraper.fetch_church_new_hymns_catalog()
    print(f"Catalog fetched: {len(catalog)} items.")
