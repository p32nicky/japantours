from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json, os

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)

def load_tours():
    with open(os.path.join(BASE_DIR, "tours.json"), encoding="utf-8") as f:
        return json.load(f)

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

    img_html = f'<img src="{img}" alt="{title}" class="hero-img">' if img else ""
    hl_html = ""
    if highlights:
        hl_html = "<div class='section'><h2>Highlights</h2><ul>" + "".join(f"<li>{h}</li>" for h in highlights) + "</ul></div>"

    book_box = f"""<div class="book-box">
      {f'<p class="price">From {price}</p>' if price else ""}
      <a href="{affiliate}" class="btn" target="_blank" rel="nofollow noopener">Book on Rakuten Travel →</a>
      <p class="note">Affiliate link — we may earn a small commission at no extra cost to you.</p>
    </div>"""

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


@app.get("/", response_class=HTMLResponse)
async def index():
    tours = load_tours()
    cards = ""
    for t in tours:
        img_html = f'<img src="{t["image"]}" style="width:100%;height:160px;object-fit:cover" alt="{t["title"]}">' if t.get("image") else '<div style="width:100%;height:160px;background:#e8e0d0;display:flex;align-items:center;justify-content:center;font-size:2.5rem">🗾</div>'
        cards += f"""<a href="/tour/{t['id']}" style="display:block;background:#fff;border-radius:10px;overflow:hidden;margin-bottom:16px;text-decoration:none;color:#222;box-shadow:0 2px 8px rgba(0,0,0,.08)">
            {img_html}
            <div style="padding:14px">
              <strong style="font-size:.95rem;line-height:1.3">{t['title']}</strong>
              <br><small style="color:#c0392b">{t.get('price','')}</small>
              <small style="color:#888;margin-left:8px">📍 {t.get('location','Japan')}</small>
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
async def tour_detail(experience_id: str):
    tours = load_tours()
    t = next((x for x in tours if x["id"] == experience_id), None)
    if not t:
        return HTMLResponse("Tour not found", status_code=404)
    return tour_page(t)
