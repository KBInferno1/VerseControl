import re
import json
import urllib.request

url = "https://www.churchofjesuschrist.org/study/manual/hymns?lang=eng"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

print(f"Fetching 1985 Hymnal index from {url}...")
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')

href_matches = re.findall(r'href="(/study/manual/hymns/[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
print(f"Found {len(href_matches)} total links.")

hymns_dict = {}

for href, inner_html in href_matches:
    # Clean inner html tags
    clean_text = re.sub(r'<[^>]+>', ' ', inner_html).strip()
    
    # Extract song number and title
    num_match = re.search(r'^\s*(\d+)\s+(.+)$', clean_text)
    if num_match:
        num = int(num_match.group(1))
        title = num_match.group(2).strip()
        if 1 <= num <= 341:
            full_url = f"https://www.churchofjesuschrist.org{href}" if href.startswith("/") else href
            hymns_dict[num] = {
                "hymn_number": num,
                "title": title,
                "url": full_url
            }

hymns_list = [hymns_dict[k] for k in sorted(hymns_dict.keys())]
print(f"Successfully extracted {len(hymns_list)} unique 1985 hymns (from #1 to #{hymns_list[-1]['hymn_number'] if hymns_list else 0}).")

# Generate static JSON seed
seed_data = []
for h in hymns_list:
    seed_data.append({
        "hymn_number": h["hymn_number"],
        "title": h["title"],
        "url": h["url"],
        "lyrics": f"Verse 1: {h['title']} - Hymn #{h['hymn_number']} from the 1985 Hymnal of The Church of Jesus Christ of Latter-day Saints."
    })

with open("db/hymns_1985_seed.json", "w", encoding="utf-8") as f:
    json.dump(seed_data, f, indent=2, ensure_ascii=False)

print(f"Saved {len(seed_data)} static 1985 hymns to db/hymns_1985_seed.json!")
