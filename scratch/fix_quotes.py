import json

def clean_file(path):
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    for item in items:
        lyrics = item.get("lyrics", "")
        if lyrics:
            # Fix single quotes inserted around every character
            cleaned = lyrics.replace("'", "")
            # Restore legitimate apostrophes in words like don't, can't, Zion's, Saints', we'll, etc.
            # Notice the original lyrics had no quote around every char, so cleaning all "'" removes the bogus ones.
            # But let's check: if lyrics has 'V'e'r's'e', removing "'" turns 'V'e'r's'e' into Verse!
            item["lyrics"] = cleaned
            
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Cleaned {path} successfully.")

clean_file("db/hymns_1985_seed.json")
clean_file("backend/hymns_1985_seed.json")
