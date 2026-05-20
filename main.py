from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import json, os

app = FastAPI()

BASE_DIR = os.path.dirname(__file__)

def load_tours():
    with open(os.path.join(BASE_DIR, "tours.json"), encoding="utf-8") as f:
        return json.load(f)

def tour_page(tour):
    title = tour["title"]
    desc = tour.get("description", "")
    img = tour.get("image", "")
    price = tour.get("price", "")
    affiliate = tour["affiliate_link"]

    img_html = f'<img src="{img}" alt="{title}" style="width:100%;max-height:400px;object-fit:cover;border-radius:12px;margin-bottom:24px">' if img else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title} — Japan Tours</title>
  <meta name="description" content="{desc[:160]}"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{desc[:160]}"/>
  {"<meta property='og:image' content='" + img + "'/>" if img else ""}
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:system-ui,sans-serif;background:#f5f5f5;color:#222;min-height:100vh}}
    header{{background:#c0392b;padding:16px 24px}}
    header a{{color:#fff;text-decoration:none;font-weight:700;font-size:1.1rem}}
    main{{max-width:800px;margin:32px auto;padding:0 20px}}
    h1{{font-size:1.8rem;line-height:1.3;margin-bottom:16px}}
    .price{{font-size:1.1rem;color:#c0392b;font-weight:700;margin-bottom:16px}}
    .desc{{line-height:1.7;color:#444;margin-bottom:32px}}
    .btn{{display:inline-block;background:#c0392b;color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:700;font-size:1.05rem}}
    .btn:hover{{background:#a93226}}
    .note{{font-size:.8rem;color:#999;margin-top:12px}}
    footer{{text-align:center;padding:24px;font-size:.82rem;color:#888;margin-top:48px}}
  </style>
</head>
<body>
  <header><a href="/">🗾 Japan Tours</a></header>
  <main>
    {img_html}
    <h1>{title}</h1>
    {f'<p class="price">From {price}</p>' if price else ""}
    {f'<p class="desc">{desc}</p>' if desc else ""}
    <a href="{affiliate}" class="btn" target="_blank" rel="nofollow noopener">Book This Experience →</a>
    <p class="note">Affiliate link — we may earn a commission at no extra cost to you.</p>
  </main>
  <footer>Japan Tours — Discover the best experiences in Japan</footer>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    tours = load_tours()
    cards = ""
    for t in tours:
        cards += f"""<a href="/tour/{t['id']}" style="display:block;background:#fff;border-radius:10px;padding:16px;margin-bottom:16px;text-decoration:none;color:#222;box-shadow:0 2px 8px rgba(0,0,0,.08)">
            <strong>{t['title']}</strong>
            {f"<br><small style='color:#c0392b'>{t['price']}</small>" if t.get('price') else ""}
        </a>"""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Japan Tours</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:system-ui,sans-serif;background:#f5f5f5}}
header{{background:#c0392b;padding:16px 24px;color:#fff;font-weight:700;font-size:1.1rem}}
main{{max-width:800px;margin:32px auto;padding:0 20px}}</style></head>
<body><header>🗾 Japan Tours</header><main><h1 style="margin-bottom:24px">Japan Experiences</h1>{cards}</main></body></html>"""


@app.get("/tour/{experience_id}", response_class=HTMLResponse)
async def tour(experience_id: str):
    tours = load_tours()
    t = next((x for x in tours if x["id"] == experience_id), None)
    if not t:
        return HTMLResponse("Tour not found", status_code=404)
    return tour_page(t)
