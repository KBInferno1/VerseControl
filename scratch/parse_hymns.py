import re
import json
import urllib.request

url = "https://www.churchofjesuschrist.org/study/manual/hymns?lang=eng"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')

print("HTML length:", len(html))

# Look for hymn hrefs or manifest entries
matches = re.findall(r'"uri":"(/study/manual/hymns/[^"]+)"[^}]*"title":"([^"]+)"', html)
print("URI-Title JSON matches:", len(matches))
if matches:
    print("Sample:", matches[:5])

# Also look for hrefs
href_matches = re.findall(r'href="(/study/manual/hymns/[^"]+)"[^>]*>(.*?)</a>', html)
print("HREF matches:", len(href_matches))
if href_matches:
    print("Sample href:", href_matches[:5])
