"""Post 25 Japan tours to Reddit - runs in GitHub Actions."""
import praw, json, os, time, csv

CLIENT_ID = "weFtQwJPb1wsdq2IXexp7Q"
CLIENT_SECRET = "a-mqkbBtpHICVo--xQWIAPENM_bSUw"
USERNAME = "Basic-Strain-6922"
PASSWORD = "Nd2354zx!!??"
SUBREDDIT = "TourJapan"
TOURS_JSON = "tours.json"
CSV_FILE = "japan_tours.csv"
POSTED_FILE = "posted_ids.txt"
BATCH = 25

def get_posted():
    if not os.path.exists(POSTED_FILE): return set()
    with open(POSTED_FILE) as f: return set(f.read().splitlines())

def mark_posted(exp_id):
    with open(POSTED_FILE, "a") as f: f.write(exp_id + "\n")

def load_rich():
    if not os.path.exists(TOURS_JSON): return {}
    with open(TOURS_JSON, encoding="utf-8") as f:
        return {t["id"]: t for t in json.load(f)}

def load_all_tours():
    """Load all tours from CSV, enrich with scraped data if available."""
    rich = load_rich()
    tours = []
    with open(CSV_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            eid = row["experience_id"]
            if eid in rich:
                tours.append(rich[eid])
            else:
                tours.append({
                    "id": eid,
                    "title": row.get("title", ""),
                    "price": row.get("price_jpy", ""),
                    "location": row.get("location", "Japan"),
                    "affiliate_link": row.get("affiliate_link", ""),
                })
    return tours

def main():
    tours = load_all_tours()
    posted_ids = get_posted()
    unposted = [t for t in tours if t["id"] not in posted_ids]

    if not unposted:
        print("All posted — resetting...")
        open(POSTED_FILE, "w").close()
        unposted = tours

    batch = unposted[:BATCH]
    print(f"Posting {len(batch)} tours to r/{SUBREDDIT} ({len(unposted)} unposted of {len(tours)} total)...")

    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
        username=USERNAME, password=PASSWORD, user_agent="TourJapan poster v1.0")
    sub = reddit.subreddit(SUBREDDIT)
    posted = 0

    for i, tour in enumerate(batch):
        title = tour.get("title", "").replace("[PR] ", "").strip()
        title = title.encode("ascii", "ignore").decode("ascii").strip()
        if not title or len(title) < 5: continue

        exp_id = tour["id"]
        location = tour.get("location", "Japan")
        # Skip bad location values
        if any(x in location for x in ["Same-Day", "Instant", "Booking", "Confirmation"]):
            location = "Japan"
        price = tour.get("price", "") or tour.get("price_jpy", "")
        site_url = f"https://japantours-site.vercel.app/tour/{exp_id}"

        body = f"""{location}, Japan | From {price}

More info & booking: {site_url}
"""
        try:
            sub.submit(title=title, selftext=body)
            mark_posted(exp_id)
            posted += 1
            print(f"[{i+1}/{len(batch)}] {title[:60]}")
        except Exception as e:
            print(f"[{i+1}/{len(batch)}] FAIL: {e}")

        time.sleep(30)

    print(f"\nDone. Posted {posted}/{len(batch)}.")

if __name__ == "__main__":
    main()
