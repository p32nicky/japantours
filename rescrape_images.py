"""Re-scrape images for tours that have blank image fields."""
import asyncio, json, os
from playwright.async_api import async_playwright

_DIR = os.path.dirname(os.path.abspath(__file__))
TOURS_JSON = os.path.join(_DIR, "tours.json")

IMG_DOMAINS = ["prod-rte-static","cloudfront.net","linktivity.io","rakuten","activityjapan.com","imgix","imagedelivery"]
IMG_SKIP    = ["logo","svg","icon","cookie"]

async def get_image(page, exp_id):
    url = f"https://experiences.travel.rakuten.com/experiences/{exp_id}"
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(4000)
    for el in await page.query_selector_all("img"):
        src = await el.get_attribute("src") or ""
        if (src.startswith("http")
                and not any(x in src for x in IMG_SKIP)
                and any(x in src for x in IMG_DOMAINS)):
            return src
    return ""

async def main():
    with open(TOURS_JSON, encoding="utf-8") as f:
        tours = json.load(f)

    no_img = [t for t in tours if not t.get("image","")]
    print(f"Tours missing image: {len(no_img)}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        fixed = 0

        for i, t in enumerate(no_img):
            for attempt in range(2):
                try:
                    img = await get_image(page, t["id"])
                    if img:
                        t["image"] = img
                        fixed += 1
                    break
                except Exception as e:
                    print(f"  [{i+1}/{len(no_img)}] {t['id']} err: {str(e)[:50]}")
                    await asyncio.sleep(3)
                    try: page = await browser.new_page()
                    except: pass

            if (i+1) % 50 == 0:
                with open(TOURS_JSON, "w", encoding="utf-8") as f:
                    json.dump(tours, f, ensure_ascii=False, indent=2)
                print(f"[{i+1}/{len(no_img)}] saved — {fixed} fixed so far")

        await browser.close()

    with open(TOURS_JSON, "w", encoding="utf-8") as f:
        json.dump(tours, f, ensure_ascii=False, indent=2)
    print(f"\nDone. Fixed {fixed}/{len(no_img)} images.")

asyncio.run(main())
