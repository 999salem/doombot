#!/usr/bin/env python3
"""Build a small JSON feed from public Google News RSS searches.
The GitHub Action runs this server-side, avoiding browser CORS limitations.
Only titles/links/dates/snippets are stored; original publishers own their content.
"""
import json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "signals.json"
UA = "Mozilla/5.0 (compatible; 999SALEM-DoomsdayTracker/1.0)"
QUERIES = [
    ('official', 'site:marvel.com/articles "Avengers: Doomsday" (trailer OR clip OR footage OR teaser OR announcement)'),
    ('official', 'site:youtube.com "Avengers: Doomsday" (Marvel Studios OR Marvel Entertainment) (trailer OR clip OR special look)'),
    ('official', 'site:video.disney.com "Avengers: Doomsday"'),
    ('official', 'site:thewaltdisneycompany.com "Avengers: Doomsday"'),
    ('news', '"Avengers: Doomsday" (new trailer OR new clip OR footage OR teaser OR featurette)'),
]
KEYWORDS = re.compile(r'(avengers.{0,15}doomsday|doomsday.{0,15}avengers)', re.I)
MEDIA = re.compile(r'(trailer|teaser|clip|footage|special look|featurette|behind.the.scenes|announcement|official|release date|interview)', re.I)

def get_text(el, path):
    child = el.find(path)
    return (child.text or '').strip() if child is not None else ''

def parse_date(value):
    if not value: return None
    try: return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except Exception: return None

def source_name(url, fallback):
    host = urllib.parse.urlparse(url).netloc.lower()
    if 'marvel.com' in host: return 'Marvel.com'
    if 'youtube.com' in host or 'youtu.be' in host: return 'YouTube / Marvel'
    if 'disney.com' in host: return 'Disney'
    if 'd23.com' in host: return 'D23'
    if 'abcnews.go.com' in host: return 'ABC News'
    return host.removeprefix('www.') or fallback or 'Online source'

items, seen = [], set()
for kind, query in QUERIES:
    rss_url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({
        'q': query, 'hl': 'en-CA', 'gl': 'CA', 'ceid': 'CA:en'
    })
    req = urllib.request.Request(rss_url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            xml = response.read()
        root = ET.fromstring(xml)
    except Exception as exc:
        print(f"RSS query failed: {query}: {exc}")
        continue
    for entry in root.findall('.//item'):
        title = get_text(entry, 'title')
        url = get_text(entry, 'link')
        published = parse_date(get_text(entry, 'pubDate'))
        desc = re.sub('<[^>]+>', ' ', get_text(entry, 'description'))
        desc = re.sub(r'\s+', ' ', desc).strip()
        if not title or not url or not KEYWORDS.search(title + ' ' + desc):
            continue
        # Avoid unrelated casting chatter dominating a trailer/clip tracker.
        if not MEDIA.search(title + ' ' + desc):
            continue
        normalized = url.split('&ved=')[0]
        if normalized in seen: continue
        seen.add(normalized)
        host = urllib.parse.urlparse(url).netloc.lower()
        publisher = get_text(entry, 'source')
        is_official = kind == 'official' or any(x in host for x in ('marvel.com','youtube.com','disney.com','d23.com'))
        items.append({
            'title': title,
            'url': url,
            'source': publisher or source_name(url, ''),
            'published': published,
            'type': 'official' if is_official else 'news',
            'category': 'Trailer / clip / announcement',
            'summary': desc[:240]
        })

items.sort(key=lambda item: item.get('published') or '', reverse=True)
payload = {'updatedAt': datetime.now(timezone.utc).isoformat(), 'items': items[:60]}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f"Wrote {len(payload['items'])} signals to {OUT}")
