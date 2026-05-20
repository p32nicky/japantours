"""Post 25 Japan tours to Reddit - runs in GitHub Actions."""
import praw, json, os, time

CLIENT_ID = "weFtQwJPb1wsdq2IXexp7Q"
CLIENT_SECRET = "a-mqkbBtpHICVo--xQWIAPENM_bSUw"
USERNAME = "Basic-Strain-6922"
PASSWORD = "Nd2354zx!!??"
SUBREDDIT = "TourJapan"
TOURS_JSON = "tours.json"
POSTED_FILE = "posted_ids.txt"
BATCH = 25

def get_posted():
    if not os.path.exists(POSTED_FILE): return set()
    with open(POSTED_FILE) as f: return set(f.read().splitlines())

def mark_posted(exp_id):
    with open(POSTED_FILE, "a") as f: f.write(exp_id + "\n")

def main():
    with open(TOURS_JSON, encoding="utf-8") as f:
        tours = json.load(f)

    posted_ids = get_posted()
    unposted = [t for t in tours if t["id"] not in posted_ids]

    if not unposted:
        print("All posted — resetting...")
        open(POSTED_FILE, "w").close()
        unposted = tours

    batch = unposted[:BATCH]
    print(f"Posting {len(batch)} tours to r/{SUBREDDIT}...")

    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
        username=USERNAME, password=PASSWORD, user_agent="TourJapan poster v1.0")
    sub = reddit.subreddit(SUBREDDIT)
    posted = 0

    for i, tour in enumerate(batch):
        title = tour.get("title", "").replace("[PR] ", "").strip()
        title = title.encode("ascii", "ignore").decode("ascii").strip()
        if not title: continue

        location = tour.get("location", "Japan")
        price = tour.get("price", "")
        exp_id = tour["id"]
        site_url = f"https://japantours-site.vercel.app/tour/{exp_id}"

        body = f"""{location}, Japan | From {price}

More info & booking: {site_url}
"""
        try:
            submission = sub.submit(title=title, selftext=body)
            mark_posted(exp_id)
            posted += 1
            print(f"[{i+1}/{len(batch)}] {title[:60]}")
        except Exception as e:
            print(f"[{i+1}/{len(batch)}] FAIL: {e}")

        time.sleep(30)

    print(f"\nDone. Posted {posted}/{len(batch)}.")

if __name__ == "__main__":
    main()
