import urllib.request
import re
import json

def fetch_lyrics(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Look for article or main or body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        if not body_match:
            return None
        body = body_match.group(1)
        
        # Extract verses: lines starting with '1.', '2.', '3.', or <p class="verse">
        # Remove script and style tags
        text_clean = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
        text_clean = re.sub(r'<style[^>]*>.*?</style>', '', text_clean, flags=re.DOTALL)
        text_clean = re.sub(r'<[^>]+>', '\n', text_clean)
        lines = [l.strip() for l in text_clean.split('\n') if l.strip()]
        
        # Locate start of song (after number & title)
        # Find verse blocks (e.g. '1.', 'Verse 1', '2.', etc.)
        verses = []
        current_verse = []
        recording = False
        
        for line in lines:
            if re.match(r'^(Text:|Music:|Composer:|Author:|\d{1,3}\.\d|\w+\s+\d+:\d+)', line):
                if current_verse:
                    verses.append("\n".join(current_verse))
                    current_verse = []
                break
            
            # Check for verse marker: '1.', '2.', 'Verse 1:'
            if re.match(r'^(\d+\.|Verse\s+\d+:?)$', line):
                if current_verse:
                    verses.append("\n".join(current_verse))
                    current_verse = []
                current_verse.append(f"Verse {re.sub(r'[^0-9]', '', line)}:")
                recording = True
                continue
            
            if recording and line:
                # Ignore UI lines
                if line in ["Lyrics Only", "PDF Sheet Music", "Contents", "Audio", "Print"]:
                    continue
                current_verse.append(line)
        
        if current_verse:
            verses.append("\n".join(current_verse))
        
        return "\n\n".join(verses) if verses else None
    except Exception as e:
        print("Error fetching", url, e)
        return None

# Test on Hymn #3 and #6 and #30
for test_url in [
    "https://www.churchofjesuschrist.org/study/manual/hymns/now-let-us-rejoice?lang=eng&platform=web",
    "https://www.churchofjesuschrist.org/study/manual/hymns/redeemer-of-israel?lang=eng&platform=web",
    "https://www.churchofjesuschrist.org/study/manual/hymns/come-come-ye-saints?lang=eng&platform=web"
]:
    print("================================")
    print("URL:", test_url)
    lyrics = fetch_lyrics(test_url)
    print(lyrics)
