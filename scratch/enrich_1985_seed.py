import urllib.request
import re
import json
import os
import time

def fetch_hymn_lyrics(url):
    try:
        # Append platform=web if missing for consistent rendering
        target_url = url if 'platform=web' in url else f"{url}&platform=web" if '?' in url else f"{url}?platform=web"
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        if not body_match:
            return None
        body = body_match.group(1)
        
        text_clean = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
        text_clean = re.sub(r'<style[^>]*>.*?</style>', '', text_clean, flags=re.DOTALL)
        text_clean = re.sub(r'<[^>]+>', '\n', text_clean)
        lines = [l.strip() for l in text_clean.split('\n') if l.strip()]
        
        verses = []
        current_verse = []
        recording = False
        
        for line in lines:
            if re.match(r'^(Text:|Music:|Composer:|Author:|\d{1,3}\.\d|\w+\s+\d+:\d+)', line):
                if current_verse:
                    verses.append("\n".join(current_verse))
                    current_verse = []
                break
            
            if re.match(r'^(\d+\.|Verse\s+\d+:?)$', line):
                if current_verse:
                    verses.append("\n".join(current_verse))
                    current_verse = []
                num = re.sub(r'[^0-9]', '', line)
                current_verse.append(f"Verse {num}:" if num else line)
                recording = True
                continue
            
            if recording and line:
                if line in ["Lyrics Only", "PDF Sheet Music", "Contents", "Audio", "Print"]:
                    continue
                current_verse.append(line)
        
        if current_verse:
            verses.append("\n".join(current_verse))
        
        if verses:
            full_text = "\n\n".join(verses)
            # Fix unicode smart quotes
            full_text = full_text.replace('', "'").replace('’', "'").replace('“', '"').replace('”', '"')
            return full_text
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    json_path = "db/hymns_1985_seed.json"
    if not os.path.exists(json_path):
        print(f"File {json_path} not found.")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    print(f"Loaded {len(items)} items from {json_path}. Enriching lyrics...")
    updated_count = 0
    
    for i, item in enumerate(items):
        current_lyrics = item.get("lyrics", "")
        # Check if lyrics are placeholder
        if "from the 1985 Hymnal of The Church" in current_lyrics or "cataloged from 1985 Hymnal" in current_lyrics or not current_lyrics:
            url = item.get("url")
            if url:
                print(f"[{i+1}/{len(items)}] Scraping #{item['hymn_number']} {item['title']}...")
                scraped = fetch_hymn_lyrics(url)
                if scraped:
                    item["lyrics"] = scraped
                    updated_count += 1
                time.sleep(0.1)
    
    print(f"Successfully enriched {updated_count} hymns with real multi-verse lyrics!")
    
    # Save back to db/hymns_1985_seed.json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    # Save copy to backend/hymns_1985_seed.json if exists or copy
    backend_path = "backend/hymns_1985_seed.json"
    with open(backend_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
        
    print(f"Saved updated seed files to {json_path} and {backend_path}.")

if __name__ == "__main__":
    main()
