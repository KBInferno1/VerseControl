import os
import re
import json
import time
import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHURCH_MUSIC_LIBRARY_URL = "https://www.churchofjesuschrist.org/study/music/hymns-for-home-and-church"
CHURCH_1985_INDEX_URL = "https://www.churchofjesuschrist.org/study/manual/hymns?lang=eng"

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

# Curated Traditional Christian Original Hymns Dataset
ORIGINAL_HYMNS_DATA = [
    {
        "title": "Joy to the World",
        "original_author": "Isaac Watts",
        "publication_year": 1719,
        "original_source": "Psalms of David Imitated in the Language of the New Testament",
        "lyrics": """Verse 1: Joy to the world, the Lord is come! Let earth receive her King; Let ev'ry heart prepare him room, And heav'n and nature sing.
Verse 2: Joy to the earth, the Savior reigns! Let men their songs employ; While fields and floods, rocks, hills, and plains Repeat the sounding joy.
Verse 3: No more let sins and sorrows grow, Nor thorns infest the ground; He comes to make his blessings flow Far as the curse is found.
Verse 4: He rules the world with truth and grace, And makes the nations prove The glories of his righteousness, And wonders of his love.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Easter/Christmas"
    },
    {
        "title": "How Firm a Foundation",
        "original_author": "Rippon's Selection (K.)",
        "publication_year": 1787,
        "original_source": "A Selection of Hymns from the Best Authors",
        "lyrics": """Verse 1: How firm a foundation, ye saints of the Lord, Is laid for your faith in his excellent word! What more can he say than to you he hath said, Who unto the Savior for refuge have fled?
Verse 2: In ev'ry condition—in sickness, in health, In poverty's vale, or abounding in wealth, At home and abroad, on the land, on the sea, As thy days may demand, so thy succor shall be.
Verse 3: Fear not, I am with thee; oh be not dismayed, For I am thy God and will still give thee aid. I'll strengthen thee, help thee, and cause thee to stand, Upheld by my righteous, omnipotent hand.
Verse 4: When through the deep waters I call thee to go, The rivers of sorrow shall not overflow; For I will be with thee thy troubles to bless, And sanctify to thee thy deepest distress.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "All People That on Earth Do Dwell",
        "original_author": "William Kethe",
        "publication_year": 1561,
        "original_source": "Anglo-Genevan Psalter",
        "lyrics": """Verse 1: All people that on earth do dwell, Sing to the Lord with cheerful voice. Him serve with fear, his praise forthtell; Come ye before him and rejoice.
Verse 2: The Lord, ye know, is God indeed; Without our aid he did us make. We are his folk, he doth us feed, And for his sheep he doth us take.
Verse 3: O enter then his gates with praise; Approach with joy his courts unto. Praise, laud, and bless his name always, For it is seemly so to do.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "Come, Thou Fount of Every Blessing",
        "original_author": "Robert Robinson",
        "publication_year": 1758,
        "original_source": "A Collection of Hymns for the Use of the Church of Christ",
        "lyrics": """Verse 1: Come, thou Fount of every blessing, Tune my heart to sing thy grace; Streams of mercy, never ceasing, Call for songs of loudest praise. Teach me some melodious sonnet, Sung by flaming tongues above. Praise the mount! I'm fixed upon it, Mount of thy redeeming love.
Verse 2: Here I raise my Ebenezer; Hither by thy help I'm come; And I hope, by thy good pleasure, Safely to arrive at home. Jesus sought me when a stranger, Wandering from the fold of God; He, to rescue me from danger, Interposed his precious blood.
Verse 3: O to grace how great a debtor Daily I'm constrained to be! Let thy goodness, like a fetter, Bind my wandering heart to thee. Prone to wander, Lord, I feel it, Prone to leave the God I love; Here's my heart, O take and seal it, Seal it for thy courts above.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    }
]

# Baseline 1985 LDS Hymnal Dataset
HYMNS_1985_DATA = [
    {
        "hymn_number": 1,
        "title": "The Morning Breaks",
        "lyrics": """Verse 1: The morning breaks, the shadows flee; Lo, Zion’s standard is unfurled! The dawning of a brighter day, The dawning of a brighter day Majestic rises on the world.
Verse 2: The clouds of error disappear Before the rays of truth divine; The glory bursting from afar, The glory bursting from afar Wide o’er the nations soon will shine.
Verse 3: The Gentile fullness now comes in, And Israel’s blessings are at hand. His covenant for the latter day, His covenant for the latter day Has dawned upon the favored land.""",
        "major_theme": "LDS-specific",
        "minor_theme": "Restoration"
    },
    {
        "hymn_number": 2,
        "title": "The Spirit of God",
        "lyrics": """Verse 1: The Spirit of God like a fire is burning! The latter-day glory begins to come forth; The visions and blessings of old are returning, And angels are coming to visit the earth.
Refrain: We’ll sing and we’ll shout with the armies of heaven, Hosanna, hosanna to God and the Lamb! Let glory to them in the highest be given, Henceforth and foreveramen and amen!
Verse 2: The Lord is extending the saints’ understanding, Restoring his power to the latter-day saints; The knowledge and power of God are expanding; The veil o'er the earth is beginning to burst.""",
        "major_theme": "LDS-specific",
        "minor_theme": "Restoration"
    },
    {
        "hymn_number": 19,
        "title": "We Thank Thee, O God, for a Prophet",
        "lyrics": """Verse 1: We thank thee, O God, for a prophet To guide us in these latter days. We thank thee for sending the gospel To lighten our minds with its rays. We thank thee for every blessing Bestowed by thy bounteous hand. We feel it a pleasure to serve thee And love to obey thy command.
Verse 2: When dark clouds of trouble hang o'er us And threaten our peace to destroy, There is hope smiling brightly before us, And we know that we deliver shall be. We doubt not the Lord nor his goodness; We’ve proved him in days that are past.""",
        "major_theme": "LDS-specific",
        "minor_theme": "Restoration"
    },
    {
        "hymn_number": 27,
        "title": "Praise to the Man",
        "lyrics": """Verse 1: Praise to the man who communed with Jehovah! Jesus anointed that Prophet and Seer. Blessed to open the last dispensation, Kings shall extol him, and nations revere.
Refrain: Hail to the Prophet, ascended to heaven! Traitors and tyrants now fight him in vain. Mingling with Gods, he can plan for his brethren; Death cannot conquer the hero again.
Verse 2: Praise to his memory, he died as a martyr; Honored and blest be his great-given name! Long shall his blood, which was shed by assassins, Plead unto heaven while the earth will remain.""",
        "major_theme": "LDS-specific",
        "minor_theme": "Restoration"
    },
    {
        "hymn_number": 85,
        "title": "How Firm a Foundation",
        "lyrics": """Verse 1: How firm a foundation, ye Saints of the Lord, Is laid for your faith in his excellent word! What more can he say than to you he hath said, Who unto the Savior, who unto the Savior, Who unto the Savior for refuge have fled?
Verse 2: In ev'ry condition—in sickness, in health, In poverty's vale, or abounding in wealth, At home and abroad, on the land, on the sea, As thy days may demand, as thy days may demand, As thy days may demand, so thy succor shall be.
Verse 3: Fear not, I am with thee; oh be not dismayed, For I am thy God and will still give thee aid. I'll strengthen thee, help thee, and cause thee to stand, Upheld by my righteous, upheld by my righteous, Upheld by my righteous, omnipotent hand.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "hymn_number": 116,
        "title": "Come, Come, Ye Saints",
        "lyrics": """Verse 1: Come, come, ye Saints, no toil nor labor fear; But with joy wend your way. Though hard to you this journey may appear, Grace shall be as your day. 'Tis better far for us to strive Our useless cares from us to drive; Do this, and joy your hearts will swell— All is well! All is well!
Verse 2: Why should we mourn or think our lot is hard? 'Tis not so; all is right. Why should we think to earn a great reward If we now shun the fight? Gird up your loins; fresh courage take. Our God will never us forsake; And soon we'll have this tale to tell— All is well! All is well!""",
        "major_theme": "LDS-specific",
        "minor_theme": "Pioneer"
    },
    {
        "hymn_number": 193,
        "title": "I Stand All Amazed",
        "lyrics": """Verse 1: I stand all amazed at the love Jesus offers me, Confused at the grace that so fully he proffers me. I tremble to know that for me he was crucified, That for me, a sinner, he suffered, he bled and died.
Refrain: Oh, it is wonderful that he should care for me Enough to die for me! Oh, it is wonderful, wonderful to me!
Verse 2: I marvel that he would descend from his throne divine To rescue a soul so rebellious and proud as mine, That he should extend his great love unto such as I, Sufficient to own, to redeem, and to justify.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Sacrament"
    },
    {
        "hymn_number": 201,
        "title": "Joy to the World",
        "lyrics": """Verse 1: Joy to the world, the Lord is come! Let earth receive her King; Let ev'ry heart prepare him room, And heav'n and nature sing, And heav'n and nature sing, And heav'n, and heav'n and nature sing.
Verse 2: Joy to the earth, the Savior reigns! Let men their songs employ; While fields and floods, rocks, hills, and plains Repeat the sounding joy, Repeat the sounding joy, Repeat, repeat the sounding joy.
Verse 3: Rejoice! Rejoice when Jesus reigns, And saints their songs employ; While fields and floods, rocks, hills, and plains Repeat the sounding joy.
Verse 4: He rules the world with truth and grace, And makes the nations prove The glories of his righteousness, And wonders of his love, And wonders of his love, And wonders, wonders of his love.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Easter/Christmas"
    },
    {
        "hymn_number": 301,
        "title": "I Am a Child of God",
        "lyrics": """Verse 1: I am a child of God, And he has sent me here, Has given me an earthly home With parents kind and dear.
Refrain: Lead me, guide me, walk beside me, Help me find the way. Teach me all that I must do To live with him someday.
Verse 2: I am a child of God, And so my needs are great; Help me to understand his word Before it is too late.""",
        "major_theme": "LDS-specific",
        "minor_theme": "Restoration"
    }
]

class HymnScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def fetch_1985_hymns_from_church_index(self) -> List[Dict[str, Any]]:
        """
        Scrapes the official 1985 LDS Hymnal index directly from https://www.churchofjesuschrist.org/study/manual/hymns?lang=eng
        """
        logger.info(f"Scraping 1985 LDS Hymnal index from {CHURCH_1985_INDEX_URL}...")
        try:
            with httpx.Client(timeout=20.0, headers=self.headers, follow_redirects=True) as client:
                resp = client.get(CHURCH_1985_INDEX_URL)
                resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            hymns_found = []

            # Find all hymn links in the manual index
            links = soup.find_all("a", href=re.compile(r"/study/manual/hymns/[a-z0-9-]+"))
            for link in links:
                text = link.get_text(strip=True)
                href = link.get("href", "")
                if text and href and not href.endswith("/hymns") and not href.endswith("_manifest"):
                    num = None
                    title = text

                    # Extract number from title string (e.g., "1. The Morning Breaks" or "Joy to the World (201)")
                    match_num_start = re.search(r"^(\d+)[\.\s]+(.*)", text)
                    match_num_end = re.search(r"(.*)\s+\((\d+)\)$", text)
                    match_slug = re.search(r"-(\d+)$", href)

                    if match_num_start:
                        num = int(match_num_start.group(1))
                        title = match_num_start.group(2)
                    elif match_num_end:
                        title = match_num_end.group(1)
                        num = int(match_num_end.group(2))
                    elif match_slug:
                        num = int(match_slug.group(1))

                    if num and title:
                        full_url = f"https://www.churchofjesuschrist.org{href}" if href.startswith("/") else href
                        hymns_found.append({
                            "hymn_number": num,
                            "title": title,
                            "url": full_url
                        })

            logger.info(f"Successfully scraped {len(hymns_found)} hymns from 1985 Hymnal index.")
            return hymns_found
        except Exception as e:
            logger.error(f"Error scraping 1985 Hymnal index: {e}")
            return []

    def seed_traditional_and_1985_hymns(self) -> Dict[str, int]:
        """
        Populates Traditional Christian Original Hymns and 1985 LDS Hymns into PostgreSQL from static seed JSON.
        """
        conn = get_db_connection()
        conn.autocommit = True
        inserted_orig = 0
        inserted_1985 = 0

        # Load static 1985 seed JSON file
        seed_paths_1985 = [
            "hymns_1985_seed.json",
            "backend/hymns_1985_seed.json",
            "db/hymns_1985_seed.json",
            "/app/hymns_1985_seed.json"
        ]
        seed_data_1985 = []
        for path in seed_paths_1985:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        seed_data_1985 = json.load(f)
                    logger.info(f"Loaded {len(seed_data_1985)} static 1985 hymns from {path}")
                    break
                except Exception as e:
                    logger.error(f"Error loading {path}: {e}")

        if not seed_data_1985:
            seed_data_1985 = HYMNS_1985_DATA

        # Load static original hymns seed JSON file
        seed_paths_orig = [
            "hymns_original_seed.json",
            "backend/hymns_original_seed.json",
            "db/hymns_original_seed.json",
            "/app/hymns_original_seed.json"
        ]
        seed_data_orig = []
        for path in seed_paths_orig:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        seed_data_orig = json.load(f)
                    logger.info(f"Loaded {len(seed_data_orig)} static original hymns from {path}")
                    break
                except Exception as e:
                    logger.error(f"Error loading {path}: {e}")

        if not seed_data_orig:
            seed_data_orig = ORIGINAL_HYMNS_DATA

        try:
            with conn.cursor() as cur:
                # 1. Insert Traditional Originals
                for item in seed_data_orig:
                    cur.execute("""
                        INSERT INTO Hymns_Original (title, original_author, publication_year, original_source, lyrics, major_theme, minor_theme)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (title) DO UPDATE SET
                            original_author = EXCLUDED.original_author,
                            publication_year = EXCLUDED.publication_year,
                            lyrics = EXCLUDED.lyrics;
                    """, (
                        item["title"], item.get("original_author"), item.get("publication_year"),
                        item.get("original_source"), item["lyrics"], item.get("major_theme"), item.get("minor_theme")
                    ))
                    if cur.rowcount > 0:
                        inserted_orig += 1

                # 2. Insert Core 1985 Baseline Hymns with detailed lyrics & themes
                for item in HYMNS_1985_DATA:
                    cur.execute("SELECT id FROM Hymns_Original WHERE LOWER(title) = LOWER(%s);", (item["title"],))
                    orig_match = cur.fetchone()
                    orig_id = orig_match["id"] if orig_match else None

                    cur.execute("""
                        INSERT INTO Hymns_1985 (hymn_number, title, lyrics, major_theme, minor_theme, original_hymn_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (hymn_number) DO UPDATE SET 
                            title = EXCLUDED.title,
                            lyrics = EXCLUDED.lyrics,
                            major_theme = EXCLUDED.major_theme,
                            minor_theme = EXCLUDED.minor_theme,
                            original_hymn_id = EXCLUDED.original_hymn_id;
                    """, (
                        item["hymn_number"], item["title"], item["lyrics"],
                        item["major_theme"], item["minor_theme"], orig_id
                    ))
                    if cur.rowcount > 0:
                        inserted_1985 += 1

                # 3. Insert Static 1985 Hymns from JSON seed file (341 hymns)
                for item in seed_data_1985:
                    cur.execute("SELECT id FROM Hymns_Original WHERE LOWER(title) = LOWER(%s);", (item["title"],))
                    orig_match = cur.fetchone()
                    orig_id = orig_match["id"] if orig_match else None

                    cur.execute("""
                        INSERT INTO Hymns_1985 (hymn_number, title, lyrics, original_hymn_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (hymn_number) DO UPDATE SET
                            title = EXCLUDED.title,
                            lyrics = EXCLUDED.lyrics,
                            original_hymn_id = COALESCE(EXCLUDED.original_hymn_id, Hymns_1985.original_hymn_id);
                    """, (
                        item["hymn_number"],
                        item["title"],
                        item.get("lyrics", f"Lyrics for #{item['hymn_number']} '{item['title']}' cataloged from 1985 Hymnal."),
                        orig_id
                    ))
                    if cur.rowcount > 0:
                        inserted_1985 += 1

                # 4. Perform 3-way cross-linking between Originals, 1985 Hymns, and New Hymns
                for item in seed_data_orig:
                    cur.execute("SELECT id FROM Hymns_Original WHERE LOWER(title) = LOWER(%s);", (item["title"],))
                    orig = cur.fetchone()
                    if orig:
                        orig_id = orig["id"]
                        lds_num = item.get("lds_hymn_number")
                        if lds_num:
                            cur.execute("UPDATE Hymns_1985 SET original_hymn_id = %s, major_theme = 'Taken from Christianity' WHERE hymn_number = %s;", (orig_id, lds_num))
                        cur.execute("UPDATE Hymns_1985 SET original_hymn_id = %s, major_theme = 'Taken from Christianity' WHERE LOWER(title) = LOWER(%s);", (orig_id, item["title"]))
                        cur.execute("UPDATE Hymns_New SET original_hymn_id = %s, major_theme = 'Taken from Christianity' WHERE LOWER(title) = LOWER(%s);", (orig_id, item["title"]))

                # 5. Fill remaining unassigned themes
                cur.execute("UPDATE Hymns_1985 SET major_theme = 'Taken from Christianity' WHERE original_hymn_id IS NOT NULL;")
                cur.execute("UPDATE Hymns_1985 SET major_theme = 'LDS-specific' WHERE major_theme IS NULL;")
                cur.execute("UPDATE Hymns_New SET major_theme = 'Taken from Christianity' WHERE original_hymn_id IS NOT NULL;")
                cur.execute("UPDATE Hymns_New SET major_theme = 'LDS-specific' WHERE major_theme IS NULL;")

            conn.close()
            logger.info(f"Seeded static {inserted_orig} Traditional Hymns and {inserted_1985} 1985 Hymns.")
            return {"inserted_original": inserted_orig, "inserted_1985": inserted_1985}
        except Exception as e:
            logger.error(f"Error seeding hymns dataset: {e}")
            return {"inserted_original": inserted_orig, "inserted_1985": inserted_1985}

    def fetch_church_new_hymns_catalog(self) -> List[Dict[str, Any]]:
        """
        Polls the Church digital music library for newly released hymns in 'Hymns—for Home and Church'.
        """
        logger.info(f"Polling Church Music Library at {CHURCH_MUSIC_LIBRARY_URL}...")
        try:
            with httpx.Client(timeout=15.0, headers=self.headers, follow_redirects=True) as client:
                response = client.get(CHURCH_MUSIC_LIBRARY_URL)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            hymns_found = []

            links = soup.find_all("a", href=re.compile(r"/study/music/hymns-for-home-and-church/"))
            for link in links:
                title_text = link.get_text(strip=True)
                href = link.get("href", "")
                if title_text and href:
                    match = re.search(r"^(\d+)\.\s*(.*)", title_text)
                    if match:
                        num = int(match.group(1))
                        title = match.group(2)
                    else:
                        num = 1000 + len(hymns_found) + 1
                        title = title_text

                    full_url = f"https://www.churchofjesuschrist.org{href}" if href.startswith("/") else href

                    hymns_found.append({
                        "hymn_number": num,
                        "title": title,
                        "url": full_url,
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
            with httpx.Client(timeout=10.0, headers=self.headers, follow_redirects=True) as client:
                resp = client.get(url)
                resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            verses = soup.find_all(["div", "p"], class_=re.compile(r"verse|stanza|body"))
            if verses:
                return "\n".join([v.get_text(separator=" ", strip=True) for v in verses])
            
            main_body = soup.find("main") or soup.find("article")
            if main_body:
                return main_body.get_text(separator="\n", strip=True)
            
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Failed to fetch lyrics from {url}: {e}")
            return ""

    def save_new_hymn_to_db(self, hymn_data: Dict[str, Any]) -> Optional[int]:
        """
        Saves or updates a new hymn entry in PostgreSQL and auto-links matching 1985 and Original records.
        """
        conn = get_db_connection()
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                lyrics = hymn_data.get("lyrics")
                if not lyrics or lyrics == "Lyrics pending ingestion...":
                    if hymn_data.get("url"):
                        lyrics = self.fetch_hymn_lyrics_from_url(hymn_data["url"])
                if not lyrics:
                    lyrics = "Lyrics pending ingestion..."

                # Match with 1985 Hymns by title
                cur.execute("SELECT id, original_hymn_id FROM Hymns_1985 WHERE LOWER(title) = LOWER(%s);", (hymn_data["title"],))
                match_1985 = cur.fetchone()
                hymn_1985_id = match_1985["id"] if match_1985 else None

                # Match with Original Hymns
                cur.execute("SELECT id FROM Hymns_Original WHERE LOWER(title) = LOWER(%s);", (hymn_data["title"],))
                match_orig = cur.fetchone()
                orig_id = match_orig["id"] if match_orig else (match_1985.get("original_hymn_id") if match_1985 else None)

                # Auto-discover traditional Christian original precursor if missing
                if not orig_id and lyrics and lyrics != "Lyrics pending ingestion...":
                    try:
                        time.sleep(3.5)  # Throttle LLM discovery calls to comply with Gemini 20 RPM free tier
                        from ai_engine import discover_original_christian_hymn
                        discovered = discover_original_christian_hymn(hymn_data["title"], lyrics)
                        if discovered:
                            cur.execute("""
                                INSERT INTO Hymns_Original (title, original_author, publication_year, original_source, lyrics, major_theme, minor_theme)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (title) DO UPDATE SET original_author = EXCLUDED.original_author
                                RETURNING id;
                            """, (
                                discovered.title, discovered.original_author, discovered.publication_year,
                                discovered.original_source, discovered.lyrics, "Taken from Christianity", discovered.minor_theme
                            ))
                            disc_res = cur.fetchone()
                            if disc_res:
                                orig_id = disc_res["id"]
                                if hymn_1985_id:
                                    cur.execute("UPDATE Hymns_1985 SET original_hymn_id = %s WHERE id = %s;", (orig_id, hymn_1985_id))
                    except Exception as disc_err:
                        logger.error(f"Error in auto-discovery: {disc_err}")

                cur.execute("""
                    INSERT INTO Hymns_New (hymn_number, title, lyrics, batch_release, hymn_1985_id, original_hymn_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (hymn_number) DO UPDATE SET
                        title = EXCLUDED.title,
                        lyrics = CASE WHEN EXCLUDED.lyrics <> 'Lyrics pending ingestion...' THEN EXCLUDED.lyrics ELSE Hymns_New.lyrics END,
                        batch_release = EXCLUDED.batch_release,
                        hymn_1985_id = COALESCE(EXCLUDED.hymn_1985_id, Hymns_New.hymn_1985_id),
                        original_hymn_id = COALESCE(EXCLUDED.original_hymn_id, Hymns_New.original_hymn_id)
                    RETURNING id;
                """, (
                    hymn_data["hymn_number"],
                    hymn_data["title"],
                    lyrics,
                    hymn_data.get("batch_release", "Batch 1"),
                    hymn_1985_id,
                    orig_id
                ))
                res = cur.fetchone()
                return res["id"] if res else None
        except Exception as e:
            logger.error(f"Database insertion error: {e}")
            return None
        finally:
            conn.close()

if __name__ == "__main__":
    scraper = HymnScraper()
    print("Testing HymnScraper instance...")
    res = scraper.seed_traditional_and_1985_hymns()
    print("Seeding result:", res)
    catalog = scraper.fetch_church_new_hymns_catalog()
    print(f"Catalog fetched: {len(catalog)} items.")
