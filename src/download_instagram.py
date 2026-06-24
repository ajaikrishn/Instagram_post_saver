import instaloader
from instaloader import Post
import os
import re
from datetime import datetime

today = datetime.today().strftime("%Y-%m-%d")

input_file = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/link_folder/links.txt"
output_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change"

processed_file = os.path.join(
    output_dir,
    "Processedlinks.txt"
)

failed_file = os.path.join(
    output_dir,
    "failed_links.txt"
)

# Load processed
if os.path.exists(processed_file):
    with open(processed_file, "r") as f:
        processed_links = {
            line.strip()
            for line in f
            if line.strip()
        }
else:
    processed_links = set()

# Load failed
if os.path.exists(failed_file):
    with open(failed_file, "r") as f:
        failed_links = {
            line.strip()
            for line in f
            if line.strip()
        }
else:
    failed_links = set()

# Read input
with open(input_file, "r") as f:
    links = [
        line.strip()
        for line in f
        if line.strip()
    ]

loader = instaloader.Instaloader(
    dirname_pattern=os.path.join(
        output_dir,
        f"{today}_{{profile}}"
    ),
    filename_pattern="{date_utc}_UTC",
    save_metadata=False,
    download_comments=False,
    download_video_thumbnails=True
)

for link in links:

    if link in processed_links:
        print(f"Already processed → {link}")
        continue

    try:

        match = re.search(
            r"/(?:p|reel)/([^/]+)/",
            link
        )

        if not match:
            raise Exception("Invalid URL")

        shortcode = match.group(1)

        post = Post.from_shortcode(
            loader.context,
            shortcode
        )

        loader.download_post(
            post,
            target=post.owner_username
        )

        with open(processed_file, "a") as f:
            f.write(link + "\n")

        processed_links.add(link)

        print(f"Downloaded → {link}")

    except Exception as e:

        if link not in failed_links:

            with open(failed_file, "a") as f:
                f.write(link + "\n")

            failed_links.add(link)

        print(f"Failed → {link}")
        print(e)

print("Completed.")