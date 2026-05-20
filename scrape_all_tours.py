"""
Scrape full details for all 13k Japan tours using Playwright.
Resumable - tracks progress, saves every 10 tours.
Run: python scrape_all_tours.py
"""
import asyncio, json, re, csv, os
from playwright.async_api import async_playwright
from urllib.parse import quote

CSV_FILE = "japan_tours.csv"
TOURS_JSON = "japantours-site/tours.json"
AFF = "https://click.linksynergy.com/deeplink?id=EWtL65s2%2ftg&mid=53671&murl={}"

JAPAN_LOCATIONS = [
    "Tokyo","Osaka","Kyoto","Okinawa","Hokkaido","Hiroshima","Nara","Fukuoka",
    "Sapporo","Nagoya","Yokohama","Chiba","Saitama","Nikko","Nagano","Hakone",
    "Kamakura","Miyazaki","Kagoshima","Nagasaki","Kumamoto","Oita","Ehime","Kochi",
    "Tokushima","Kagawa","Yamaguchi","Shimane","Tottori","Okayama","Hyogo","Wakayama",
    "Mie","Shiga","Shizuoka","Yamanashi","Ibaraki","Tochigi","Gunma","Fukushima",
    "Miyagi","Akita","Yamagata","Iwate","Aomori","Aichi","Gifu","Fukui","Ishikawa",
    "Toyama","Niigata","Kanagawa","Kobe","Naha","Ginza","Shibuya","Shinjuku",
    "Asakusa","Harajuku","Ueno","Akihabara","Roppongi","Odaiba","Hakuba","Beppu",
    "Takayama","Matsumoto","Kanazawa","Atami","Izu","Nikko","Kusatsu","Karuizawa",
]

def extract_section(content, start, ends):
    m = re.search(re.escape(start) + r'\s*\n(.*?)(?=' + '|'.join(re.escape(e) for e in ends) + ')', content, re.DOTALL)
    return m.group(1).strip() if m else ""

def load_existing():
    if os.path.exists(TOURS_JSON):
        with open(TOURS_JSON, encoding="utf-8") as f:
            return {t["id"]: t for t in json.load(f)}
    return {}

def save_all(rich):
    with open(TOURS_JSON, "w", encoding="utf-8") as f:
        json.dump(list(rich.values()), f, ensure_ascii=False, indent=2)

def load_csv_ids():
    with open(CSV_FILE, encoding="utf-8") as f:
        return [row["experience_id"] for row in csv.DictReader(f)]

async def scrape_one(page, exp_id):
    url = f"https://experiences.travel.rakuten.com/experiences/{exp_id}"
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(5000)
    content = await page.inner_text("body")

    h1s = await page.query_selector_all("h1")
    title = (await h1s[1].inner_text()).strip() if len(h1s) >= 2 else (await h1s[0].inner_text()).strip() if h1s else ""

    img = ""
    for el in await page.query_selector_all("img"):
        src = await el.get_attribute("src") or ""
        if ("prod-rte-static" in src or "cloudfront.net" in src) and src.startswith("http"):
            img = src
            break

    location = "Japan"
    for loc in JAPAN_LOCATIONS:
        if loc.lower() in content[:800].lower():
            location = loc
            break

    price = ""
    m = re.search(r'([\d,]+)\s*JPY', content)
    if m: price = f"{m.group(1)} JPY"

    highlights = []
    hl_text = extract_section(content, "Highlights", ["Key Information","Important Information","Booking"])
    for line in hl_text.splitlines():
        line = line.strip()
        if line and len(line) > 5 and line not in ["Same-Day Booking","Instant Confirmation","New"]:
            highlights.append(line)

    return {
        "id": exp_id,
        "title": title,
        "overview": extract_section(content, "Overview", ["Highlights","Key Information"]),
        "highlights": highlights[:6],
        "important_info": extract_section(content, "Important Information", ["Booking","What to Bring","Description"]),
        "what_to_bring": extract_section(content, "What to Bring", ["Meeting Point","Venue Address","Schedule","Description"]),
        "meeting_point": extract_section(content, "Meeting Point", ["Venue Address","Schedule","Description","Provided by"]),
        "venue_address": extract_section(content, "Venue Address", ["Schedule","Provided by","Description"]),
        "schedule": extract_section(content, "Schedule", ["Provided by","Cancellation Policy","Description"]),
        "cancellation": extract_section(content, "Cancellation Policy", ["Description","Selected Option","Top Destination"]),
        "description": extract_section(content, "Description", ["Access","How it works","Selected Option","Top Destination"]),
        "access": extract_section(content, "Access", ["How it works","Selected Option","Top Destination"]),
        "how_it_works": extract_section(content, "How it works", ["Selected Option","Top Destination"]),
        "image": img,
        "price": price,
        "location": location,
        "url": url,
        "affiliate_link": AFF.format(quote(url, safe="")),
    }

async def main():
    all_ids = load_csv_ids()
    rich = load_existing()
    todo = [i for i in all_ids if i not in rich]
    total = len(all_ids)
    done = len(rich)
    print(f"Total: {total} | Already scraped: {done} | Remaining: {len(todo)}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        errors = 0

        for i, exp_id in enumerate(todo):
            for attempt in range(3):
                try:
                    data = await scrape_one(page, exp_id)
                    rich[exp_id] = data
                    errors = 0
                    break
                except Exception as e:
                    print(f"  [{done+i+1}/{total}] {exp_id} attempt {attempt+1} failed: {str(e)[:60]}")
                    await asyncio.sleep(5)
                    try:
                        page = await browser.new_page()
                    except:
                        pass

            if (i + 1) % 10 == 0:
                save_all(rich)
                pct = (done + i + 1) / total * 100
                print(f"[{done+i+1}/{total}] {pct:.1f}% — saved. Last: {exp_id}")

        await browser.close()

    save_all(rich)
    print(f"\nDone! Scraped {len(rich)}/{total} tours.")

asyncio.run(main())
