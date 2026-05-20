from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json, os, re

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)

def load_tours():
    with open(os.path.join(BASE_DIR, "tours.json"), encoding="utf-8") as f:
        return json.load(f)

def clean(text):
    return re.sub(r'[^\x00-\x7F]+', lambda m: m.group(0), text) if text else ""

def tour_page(tour):
    title = tour.get("title", "")
    desc = tour.get("description", "")
    img = tour.get("image", "")
    price = tour.get("price", "")
    location = tour.get("location", "Japan")
    highlights = tour.get("highlights", [])
    affiliate = tour["affiliate_link"]

    img_html = f'<img src="{img}" alt="{title}" style="width:100%;max-height:420px;object-fit:cover;border-radius:12px;margin-bottom:28px">' if img else ""

    hl_html = ""
    if highlights:
        items = "".join(f"<li>{h}</li>" for h in highlights)
        hl_html = f"<h2>Highlights</h2><ul class='highlights'>{items}</ul>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title} — Japan Tours</title>
  <meta name="description" content="{desc[:200]}"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{desc[:200]}"/>
  {"<meta property='og:image' content='" + img + "'/>" if img else ""}
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:system-ui,-apple-system,sans-serif;background:#f5f0eb;color:#222;min-height:100vh}}
    header{{background:#c0392b;padding:16px 24px}}
    header a{{color:#fff;text-decoration:none;font-weight:700;font-size:1.1rem}}
    main{{max-width:820px;margin:32px auto;padding:0 20px}}
    .badge{{display:inline-block;background:#c0392b;color:#fff;padding:4px 12px;border-radius:20px;font-size:.78rem;font-weight:700;text-transform:uppercase;margin-bottom:12px}}
    h1{{font-size:1.75rem;line-height:1.3;margin-bottom:12px}}
    .meta{{color:#888;font-size:.9rem;margin-bottom:20px}}
    .desc{{line-height:1.75;color:#444;margin-bottom:24px;font-size:1rem}}
    h2{{font-size:1.2rem;margin:24px 0 12px;color:#333}}
    ul.highlights{{padding-left:20px}}
    ul.highlights li{{margin-bottom:8px;line-height:1.5;color:#444}}
    .book-box{{background:#fff;border-radius:12px;padding:24px;margin:32px 0;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
    .price{{font-size:1.4rem;font-weight:700;color:#c0392b;margin-bottom:16px}}
    .btn{{display:inline-block;background:#c0392b;color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:700;font-size:1.05rem}}
    .btn:hover{{background:#a93226}}
    .note{{font-size:.78rem;color:#aaa;margin-top:10px}}
    footer{{text-align:center;padding:24px;font-size:.82rem;color:#888;margin-top:48px;border-top:1px solid #e0d8cc}}
  </style>
</head>
<body>
  <header><a href="/">🗾 Japan Tours</a></header>
  <main>
    {img_html}
    <span class="badge">🇯🇵 {location}</span>
    <h1>{title}</h1>
    <p class="meta">📍 {location}, Japan</p>
    {f'<p class="desc">{desc}</p>' if desc else ""}
    {hl_html}
    <div class="book-box">
      {f'<p class="price">From {price}</p>' if price else ""}
      <a href="{affiliate}" class="btn" target="_blank" rel="nofollow noopener">Book This Experience on Rakuten →</a>
      <p class="note">Affiliate link — we may earn a small commission at no extra cost to you.</p>
    </div>
  </main>
  <footer>Japan Tours — Discover the best experiences in Japan</footer>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    tours = load_tours()
    cards = ""
    for t in tours:
        img_html = f'<img src="{t["image"]}" style="width:100%;height:160px;object-fit:cover" alt="{t["title"]}">' if t.get("image") else '<div style="width:100%;height:160px;background:#e8e0d0;display:flex;align-items:center;justify-content:center;font-size:2rem">🗾</div>'
        cards += f"""<a href="/tour/{t['id']}" style="display:block;background:#fff;border-radius:10px;overflow:hidden;margin-bottom:16px;text-decoration:none;color:#222;box-shadow:0 2px 8px rgba(0,0,0,.08)">
            {img_html}
            <div style="padding:14px">
              <strong>{t['title']}</strong>
              {f"<br><small style='color:#c0392b'>{t['price']}</small>" if t.get('price') else ""}
              {f"<br><small style='color:#888'>📍 {t['location']}</small>" if t.get('location') else ""}
            </div>
        </a>"""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Japan Tours — Best Experiences in Japan</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:system-ui,sans-serif;background:#f5f0eb}}
header{{background:#c0392b;padding:16px 24px;color:#fff;font-weight:700;font-size:1.1rem}}
main{{max-width:800px;margin:32px auto;padding:0 20px}}</style></head>
<body><header>🗾 Japan Tours</header><main>
<h1 style="margin-bottom:24px;font-size:1.6rem">Best Experiences in Japan</h1>
{cards}</main></body></html>"""


@app.get("/tour/{experience_id}", response_class=HTMLResponse)
async def tour(experience_id: str):
    tours = load_tours()
    t = next((x for x in tours if x["id"] == experience_id), None)
    if not t:
        return HTMLResponse("Tour not found", status_code=404)
    return tour_page(t)
