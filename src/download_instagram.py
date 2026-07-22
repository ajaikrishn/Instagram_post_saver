import instaloader
from instaloader import Post
import pandas as pd
import os
import re
import requests
from datetime import datetime

# ---------- CONFIG ----------
input_file = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/links.txt"
output_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change"
processed_file = os.path.join(output_dir, "Processedlinks.txt")
failed_file = os.path.join(output_dir, "failed_links.txt")
records_file = os.path.join(output_dir, "downloaded_links.xlsx")

# Optional login — needed if links include private accounts / hitting rate limits.
# Uncomment and set once, instaloader will cache the session file locally.
# IG_USERNAME = "your_username"
# L_LOGIN = True

# ---------- LOAD STATE ----------
if os.path.exists(processed_file):
    with open(processed_file, "r") as f:
        processed_links = {line.strip() for line in f if line.strip()}
else:
    processed_links = set()

if os.path.exists(failed_file):
    with open(failed_file, "r") as f:
        failed_links = {line.strip() for line in f if line.strip()}
else:
    failed_links = set()

if os.path.exists(records_file):
    records_df = pd.read_excel(records_file)
    records = records_df.to_dict("records")
else:
    records = []

with open(input_file, "r") as f:
    links = [line.strip() for line in f if line.strip()]

# ---------- HELPERS ----------
def sanitize_folder_name(name: str) -> str:
    """Strip characters that break folder names on most OSes."""
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()


def clean_caption(raw_caption: str) -> str:
    """Refactor caption: drop hashtags, mentions, emoji, collapse whitespace."""
    if not raw_caption:
        return ""
    text = re.sub(r"#\w+", "", raw_caption)               # hashtags
    text = re.sub(r"@\w+", "", text)                        # mentions
    text = re.sub(r"[\U0001F300-\U0001FAFF]", "", text)     # emoji range
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------- LOADER SETUP ----------
loader = instaloader.Instaloader(
    save_metadata=False,
    download_comments=False,
    download_video_thumbnails=False,
    filename_pattern="{shortcode}",
    max_connection_attempts=3,     # stop retry after 3, not infinite
    fatal_status_codes=[400, 401, 403]
)

TOR_PROXY = "socks5h://127.0.0.1:9050"  # Tor Browser default. Standalone tor daemon = 9050.

session = requests.Session()
session.proxies = {"http": TOR_PROXY, "https": TOR_PROXY}
loader.context._session = session

# verify Tor actually route traffic before burn requests on IG
def verify_tor():
    r = session.get("https://check.torproject.org/api/ip", timeout=15)
    data = r.json()
    if not data.get("IsTor"):
        raise RuntimeError(f"Not routed through Tor! Exit IP: {data.get('IP')}")
    print(f"Tor OK. Exit IP: {data.get('IP')}")

verify_tor()

# if login needed, e.g.:
# loader.load_session_from_file(IG_USERNAME)  # after one manual `instaloader -l username` login

# ---------- MAIN LOOP ----------
for link in links:
    if link in processed_links:
        print(f"Already processed → {link}")
        continue

    try:
        match = re.search(r"/(?:p|reel)/([^/]+)/", link)
        if not match:
            raise Exception("Invalid URL")
        shortcode = match.group(1)

        post = Post.from_shortcode(loader.context, shortcode)

        profile_name = sanitize_folder_name(post.owner_username)
        dt_str = post.date_utc.strftime("%Y%m%d_%H%M%S")
        folder_name = f"{profile_name}_{dt_str}"
        target_dir = os.path.join(output_dir, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        # point instaloader straight at this post's own folder
        loader.dirname_pattern = target_dir

        before_files = set(os.listdir(target_dir))
        loader.download_post(post, target=folder_name)
        after_files = set(os.listdir(target_dir))
        new_files = sorted(after_files - before_files)

        # save cleaned caption as its own file inside the same folder
        caption_clean = clean_caption(post.caption)
        with open(os.path.join(target_dir, "caption.txt"), "w", encoding="utf-8") as cf:
            cf.write(caption_clean)

        if new_files:
            for fname in new_files:
                records.append({"link": link, "folder": folder_name, "filename": fname})
        else:
            records.append({"link": link, "folder": folder_name, "filename": None})

        pd.DataFrame(records).to_excel(records_file, index=False)

        with open(processed_file, "a") as f:
            f.write(link + "\n")
        processed_links.add(link)

        print(f"Downloaded → {link} → {folder_name}")

    except Exception as e:
        if link not in failed_links:
            with open(failed_file, "a") as f:
                f.write(link + "\n")
            failed_links.add(link)
        print(f"Failed → {link}")
        print(e)

print("Completed.")