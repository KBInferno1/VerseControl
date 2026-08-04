import json
import os
import sys

# Add backend directory to path to import ORIGINAL_HYMNS_DATA
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
try:
    from scraper import ORIGINAL_HYMNS_DATA
except ImportError:
    ORIGINAL_HYMNS_DATA = []

orig_lyrics_map = {item["title"].strip().lower(): item["lyrics"] for item in ORIGINAL_HYMNS_DATA if "lyrics" in item}

def enrich_original():
    orig_path = "db/hymns_original_seed.json"
    h1985_path = "db/hymns_1985_seed.json"

    with open(orig_path, "r", encoding="utf-8") as f:
        orig_items = json.load(f)

    with open(h1985_path, "r", encoding="utf-8") as f:
        h1985_items = json.load(f)

    h1985_map_by_num = {h["hymn_number"]: h["lyrics"] for h in h1985_items if "lyrics" in h and "from the 1985 Hymnal" not in h["lyrics"]}
    h1985_map_by_title = {h["title"].strip().lower(): h["lyrics"] for h in h1985_items if "lyrics" in h and "from the 1985 Hymnal" not in h["lyrics"]}

    updated = 0
    for item in orig_items:
        title_key = item["title"].strip().lower()
        lds_num = item.get("lds_hymn_number")

        # 1. Check curated ORIGINAL_HYMNS_DATA
        if title_key in orig_lyrics_map and "Original traditional text" not in orig_lyrics_map[title_key]:
            item["lyrics"] = orig_lyrics_map[title_key]
            updated += 1
        # 2. Check 1985 scraped real lyrics
        elif lds_num and lds_num in h1985_map_by_num:
            item["lyrics"] = h1985_map_by_num[lds_num]
            updated += 1
        elif title_key in h1985_map_by_title:
            item["lyrics"] = h1985_map_by_title[title_key]
            updated += 1

    print(f"Enriched {updated} / {len(orig_items)} original precursor hymns with real multi-verse lyrics.")

    # Save to db/hymns_original_seed.json
    with open("db/hymns_original_seed.json", "w", encoding="utf-8") as f:
        json.dump(orig_items, f, indent=2, ensure_ascii=False)

    # Save to backend/hymns_original_seed.json
    with open("backend/hymns_original_seed.json", "w", encoding="utf-8") as f:
        json.dump(orig_items, f, indent=2, ensure_ascii=False)

    print("Updated db/hymns_original_seed.json and backend/hymns_original_seed.json.")

if __name__ == "__main__":
    enrich_original()
