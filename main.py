from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json, os, csv

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)

# Load rich data (fully scraped tours)
_rich = {}
_rich_path = os.path.join(BASE_DIR, "tours.json")
if os.path.exists(_rich_path):
    for t in json.load(open(_rich_path, encoding="utf-8")):
        _rich[t["id"]] = t

# Load all tours from CSV into memory at startup
_all_tours = {}
_csv_path = os.path.join(BASE_DIR, "japan_tours.csv")
if os.path.exists(_csv_path):
    with open(_csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            _all_tours[row["experience_id"]] = row

def get_tour(exp_id):
    if exp_id in _rich:
        return _rich[exp_id]
    row = _all_tours.get(exp_id)
    if not row:
        return None
    return {
        "id": exp_id,
        "title": row.get("title", ""),
        "overview": "",
        "highlights": [],
        "important_info": "",
        "what_to_bring": "",
        "meeting_point": "",
        "venue_address": "",
        "schedule": "",
        "cancellation": "",
        "description": "",
        "access": "",
        "how_it_works": "",
        "image": "",
        "price": row.get("price_jpy", ""),
        "location": row.get("location", "Japan"),
        "url": row.get("url", ""),
        "affiliate_link": row.get("affiliate_link", ""),
    }

def load_tours():
    all_csv = [get_tour(k) for k in list(_all_tours.keys())]
    rich_ids = set(_rich.keys())
    return [_rich[t["id"]] if t["id"] in rich_ids else t for t in all_csv]

def section(title, content):
    if not content or not content.strip():
        return ""
    # Convert bullet points
    lines = content.strip().splitlines()
    paras = ""
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith("•") or line.startswith("*") or line.startswith("-"):
            paras += f"<li>{line.lstrip('•*- ').strip()}</li>"
        else:
            paras += f"<p>{line}</p>"
    if "<li>" in paras:
        paras = paras.replace("<li>", "", 1)
        paras = "<ul><li>" + paras + "</ul>"
    return f"<div class='section'><h2>{title}</h2>{paras}</div>"

def tour_page(t):
    title = t.get("title", "")
    img = t.get("image", "")
    price = t.get("price", "")
    location = t.get("location", "Japan")
    affiliate = t["affiliate_link"]
    highlights = t.get("highlights", [])

    img = img or get_fallback(clean_loc(location))
    img_html = f'<img src="{img}" alt="{title}" class="hero-img">'
    hl_html = ""
    if highlights:
        hl_html = "<div class='section'><h2>Highlights</h2><ul>" + "".join(f"<li>{h}</li>" for h in highlights) + "</ul></div>"

    book_box = f"""<div class="book-box">
      {f'<p class="price">From {price}</p>' if price else ""}
      <a href="{affiliate}" class="btn" target="_blank" rel="nofollow noopener">Book on Rakuten Travel →</a>
      <p class="note">Affiliate link — we may earn a small commission at no extra cost to you.</p>
    </div>"""

    # For CSV-only tours with no scraped content
    has_content = any([t.get("overview"), t.get("description"), t.get("highlights")])
    if not has_content:
        body_sections = (
            book_box +
            "<div class='section'><p>This is an authentic experience listed on Rakuten Travel. Click the button above to see full details, availability, and pricing on Rakuten.</p></div>" +
            book_box
        )
    else:
     body_sections = (
        book_box +
        section("Overview", t.get("overview", "")) +
        hl_html +
        section("Important Information", t.get("important_info", "")) +
        book_box +
        section("What to Bring", t.get("what_to_bring", "")) +
        section("Meeting Point", t.get("meeting_point", "")) +
        section("Venue Address", t.get("venue_address", "")) +
        section("Schedule", t.get("schedule", "")) +
        section("Cancellation Policy", t.get("cancellation", "")) +
        section("Description", t.get("description", "")) +
        section("Access", t.get("access", "")) +
        section("How it Works", t.get("how_it_works", "")) +
        book_box
     )

    desc_meta = t.get("overview", t.get("description", ""))[:200]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title} — Japan Tours</title>
  <meta name="description" content="{desc_meta}"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{desc_meta}"/>
  {"<meta property='og:image' content='" + img + "'/>" if img else ""}
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:system-ui,-apple-system,sans-serif;background:#f5f0eb;color:#222;min-height:100vh}}
    header{{background:#c0392b;padding:16px 24px}}
    header a{{color:#fff;text-decoration:none;font-weight:700;font-size:1.1rem}}
    main{{max-width:820px;margin:32px auto;padding:0 20px 48px}}
    .hero-img{{width:100%;max-height:420px;object-fit:cover;border-radius:12px;margin-bottom:24px}}
    .badge{{display:inline-block;background:#c0392b;color:#fff;padding:4px 12px;border-radius:20px;font-size:.78rem;font-weight:700;text-transform:uppercase;margin-bottom:10px}}
    h1{{font-size:1.75rem;line-height:1.3;margin-bottom:8px}}
    .meta{{color:#888;font-size:.9rem;margin-bottom:24px}}
    .section{{margin:28px 0}}
    .section h2{{font-size:1.15rem;font-weight:700;margin-bottom:12px;color:#333;border-bottom:2px solid #e0d8cc;padding-bottom:6px}}
    .section p{{line-height:1.75;color:#444;margin-bottom:8px}}
    .section ul{{padding-left:20px}}
    .section li{{margin-bottom:7px;line-height:1.6;color:#444}}
    .book-box{{background:#fff;border-radius:12px;padding:24px;margin:32px 0;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
    .price{{font-size:1.4rem;font-weight:700;color:#c0392b;margin-bottom:16px}}
    .btn{{display:inline-block;background:#c0392b;color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:700;font-size:1.05rem}}
    .btn:hover{{background:#a93226}}
    .note{{font-size:.78rem;color:#aaa;margin-top:10px}}
    .back{{display:inline-block;margin-top:32px;color:#c0392b;text-decoration:none;font-weight:600}}
    footer{{text-align:center;padding:24px;font-size:.82rem;color:#888;border-top:1px solid #e0d8cc}}
  </style>
</head>
<body>
  <header><a href="/">🗾 Japan Tours</a></header>
  <main>
    {img_html}
    <span class="badge">🇯🇵 {location}</span>
    <h1>{title}</h1>
    <p class="meta">📍 {location}, Japan</p>
    {body_sections}
    <a href="/" class="back">← Back to all tours</a>
  </main>
  <footer>Japan Tours — Discover the best experiences in Japan</footer>
</body>
</html>"""


CATEGORIES = ["Tokyo","Osaka","Kyoto","Okinawa","Hokkaido","Fukuoka","Hiroshima",
    "Nara","Yokohama","Kobe","Nagoya","Sapporo","Nagasaki","Kanazawa","Hakone",
    "Nikko","Kamakura","Gifu","Nagano","Naha"]

FALLBACK_IMAGES = {
    "Tokyo":     "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&q=70",
    "Osaka":     "https://images.unsplash.com/photo-1590559899731-a382839e5549?w=400&q=70",
    "Kyoto":     "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=400&q=70",
    "Okinawa":   "https://images.unsplash.com/photo-1590736704728-f4730bb30770?w=400&q=70",
    "Hokkaido":  "https://images.unsplash.com/photo-1578637387939-43c525550085?w=400&q=70",
    "Hiroshima": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=400&q=70",
    "Nara":      "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=400&q=70",
    "Hakone":    "https://images.unsplash.com/photo-1480796927426-f609979314bd?w=400&q=70",
}
FALLBACK_DEFAULT = "https://images.unsplash.com/photo-1480796927426-f609979314bd?w=400&q=70"

def get_fallback(loc):
    return FALLBACK_IMAGES.get(loc, FALLBACK_DEFAULT)

def clean_loc(loc):
    bad = {"Japan","Same-Day Booking","Instant Confirmation","","Booking","Confirmation","Kanagawa Prefecture"}
    if not loc or loc in bad: return "Japan"
    # Map prefectures to cities
    if "Kanagawa" in loc: return "Yokohama"
    if "Osaka" in loc: return "Osaka"
    if "Tokyo" in loc: return "Tokyo"
    if "Kyoto" in loc: return "Kyoto"
    for c in CATEGORIES:
        if c.lower() in loc.lower(): return c
    return "Japan"

@app.get("/", response_class=HTMLResponse)
async def index(q: str = "", cat: str = ""):
    all_tours = load_tours()

    # Apply clean location
    for t in all_tours:
        t["_loc"] = clean_loc(t.get("location",""))

    # Filter server-side
    filtered = all_tours
    if q:
        filtered = [t for t in filtered if q.lower() in t.get("title","").lower()]
    if cat and cat != "All":
        filtered = [t for t in filtered if t["_loc"] == cat]

    # Category counts
    from collections import Counter
    loc_counts = Counter(t["_loc"] for t in all_tours if t["_loc"] != "Japan")
    top_cats = [c for c in CATEGORIES if loc_counts.get(c,0) > 0]

    cat_buttons = f'<a href="/" class="cat-btn {"active" if not cat else ""}">All ({len(all_tours)})</a>'
    for loc in top_cats:
        active = "active" if cat == loc else ""
        cat_buttons += f'<a href="/?cat={loc}" class="cat-btn {active}">{loc} ({loc_counts[loc]})</a>'

    cards = ""
    for t in filtered[:300]:
        img = t.get("image","") or get_fallback(t.get("_loc","Japan"))
        img_html = f'<img src="{img}" alt="" loading="lazy">'
        loc = t["_loc"]
        title = t.get("title","").replace('"',"&quot;").replace("'","&#39;")
        price = t.get("price","") or t.get("price_jpy","")
        cards += f'<a href="/tour/{t["id"]}" class="card"><div class="card-img">{img_html}</div><div class="card-body"><p class="card-title">{title}</p><p class="card-meta">📍 {loc} · <span class="price">{price}</span></p></div></a>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Japan Tours — Best Experiences in Japan</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:system-ui,sans-serif;background:#f5f0eb;color:#222}}
    header{{background:#c0392b;padding:14px 24px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
    header a{{color:#fff;text-decoration:none;font-weight:700;font-size:1.1rem;white-space:nowrap}}
    .search-wrap{{display:flex;gap:8px;flex:1;max-width:420px}}
    .search-wrap input{{flex:1;padding:8px 12px;border:none;border-radius:6px;font-size:.9rem}}
    .search-wrap button{{padding:8px 14px;background:#a93226;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:600}}
    main{{max-width:1200px;margin:0 auto;padding:20px}}
    .cats{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}}
    .cat-btn{{padding:5px 14px;border:2px solid #c0392b;border-radius:20px;background:#fff;color:#c0392b;cursor:pointer;font-size:.82rem;font-weight:600}}
    .cat-btn:hover,.cat-btn.active{{background:#c0392b;color:#fff}}
    .count{{color:#888;font-size:.82rem;margin-bottom:12px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}}
    .card{{background:#fff;border-radius:10px;overflow:hidden;text-decoration:none;color:#222;box-shadow:0 2px 8px rgba(0,0,0,.08);display:flex;flex-direction:column;transition:transform .15s}}
    .card:hover{{transform:translateY(-3px)}}
    .card-img img{{width:100%;height:150px;object-fit:cover;display:block}}
    .no-img{{width:100%;height:150px;background:#e8e0d0;display:flex;align-items:center;justify-content:center;font-size:2rem}}
    .card-body{{padding:10px;flex:1}}
    .card-title{{font-size:.85rem;font-weight:600;line-height:1.35;margin-bottom:6px}}
    .card-meta{{font-size:.76rem;color:#888}}
    .price{{color:#c0392b;font-weight:700}}
    footer{{text-align:center;padding:20px;font-size:.8rem;color:#888;margin-top:24px}}
  </style>
</head>
<body>
<header>
  <a href="/">🗾 Japan Tours</a>
  <form class="search-wrap" method="get" action="/">
    <input name="q" placeholder="Search tours..." value="{q}"/>
    <button type="submit">Search</button>
  </form>
</header>
<main>
  <div class="cats">{cat_buttons}</div>
  <p class="count">Showing {min(len(filtered),300)} of {len(filtered)} experiences</p>
  <div class="grid" id="grid">{cards}</div>
</main>
<footer>Japan Tours — Discover the best experiences in Japan</footer>
<script>
function filter(loc){{
  document.querySelectorAll('.cat-btn').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.card').forEach(c=>{{
    c.style.display=(loc==='All'||c.dataset.loc===loc)?'':'none';
  }});
}}
</script>
</body></html>"""


@app.get("/tour/{experience_id}", response_class=HTMLResponse)
async def tour_detail(experience_id: str):
    t = get_tour(experience_id)
    if not t:
        return HTMLResponse("Tour not found", status_code=404)
    return tour_page(t)
