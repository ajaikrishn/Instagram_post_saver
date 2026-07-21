#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 12:10:41 2026

@author: ajai-krishna
"""
import os
import re
import json
import requests
import subprocess
from bs4 import BeautifulSoup

input_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/Outputs/html_parsed_links/"
output_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/Outputs/posts"




def _extract_bracket_json(html, key_marker):
    """Bracket-match the JSON array/object that starts right after key_marker
    (e.g. '"carousel_media":['), string-escape aware. Return parsed JSON or None."""
    idx = html.find(key_marker)
    if idx == -1:
        return None
    start = idx + len(key_marker) - 1  # position of opening [ or {
    open_ch = html[start]
    close_ch = "]" if open_ch == "[" else "}"
    depth = 0
    in_str = False
    esc = False
    for j in range(start, len(html)):
        ch = html[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return json.loads(html[start:j + 1])
    return None


def _best_url(item):
    """Return (url, is_video), or None if item has neither — some carousel
    nodes are malformed/incomplete and carry no real media. Never crash here,
    one bad item shouldn't kill the whole post's downloads."""
    video_versions = item.get("video_versions")
    if video_versions:
        return video_versions[0]["url"], True
    image_versions2 = item.get("image_versions2")
    if image_versions2 and image_versions2.get("candidates"):
        return image_versions2["candidates"][0]["url"], False
    return None

def _ytdlp_fallback(page_url, folder, vid_i):
    cmd = [
        "yt-dlp",
        "--cookies-from-browser",
        "firefox:/home/ajai-krishna/setups/tor-browser-linux-x86_64-15.0.17/tor-browser/Browser/TorBrowser/Data/Browser/profile.default",
        "-P", folder,
        page_url
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True,
            timeout=120
        )

        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print("\n===== yt-dlp stdout =====")
        print(e.stdout)
        print("\n===== yt-dlp stderr =====")
        print(e.stderr)
        return False

def _video_via_bs4_ytdlp(html, page_url, folder, vid_i):
    """bs4 confirms a video exists on page (blob src useless for fetch);
    actual download goes through yt-dlp against the real post page_url."""
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("video")
    if not tag:
        return False                      # no video tag at all, skip

    src = tag.get("src", "")
    print(f"bs4 found video tag, src={src}")   # blob:... just for logging/debug

    if not page_url:
        print("No page_url to hand yt-dlp, can't fetch")
        return False

    return _ytdlp_fallback(page_url, folder, vid_i)

def _video_from_soup(html):
    """Last-resort fallback: single video/reel post. Video not paginated
    like carousel, so DOM <video src> tag reliable (unlike lazy-load imgs)."""
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("video")
    if tag and tag.get("src"):
        return tag["src"].replace("\\/", "/"), True
    return None

def get_post_media(html):
    carousel = _extract_bracket_json(html, '"carousel_media":[')
    if carousel is not None:
        results = []
        for item in carousel:
            r = _best_url(item)
            if r:
                results.append(r)
            else:
                print(f"WARNING: carousel item id={item.get('id')} has no usable media, skipped")
        return results

    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", property="og:url")
    page_url = tag.get("content") if tag else None

    if not page_url:                                      # <-- same fallback here
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            page_url = canonical["href"]

    shortcode = None
    if page_url:
        sc = re.search(r'/(?:p|reel)/([^/]+)/', page_url)
        shortcode = sc.group(1) if sc else None

    if shortcode:
        idx = html.find(f'"code":"{shortcode}"')
        if idx != -1:
            typename_idx = html.rfind('"__typename":"XIGPolaris', 0, idx)
            back = html.rfind("{", 0, typename_idx) if typename_idx != -1 else html.rfind("{", 0, idx)
            node = _extract_bracket_json(html[back:], "{")
            if node:
                r = _best_url(node)
                if r:
                    return [r]
                print("WARNING: shortcode json node has no usable media")
                
    idx = html.find(f'"code":"{shortcode}"')
    typename_idx = html.rfind('"__typename":"XIGPolaris', 0, idx)
    back = html.rfind("{", 0, typename_idx)
    print(html[back:back+400])   # see what object bracket-match actually starts at

    print("WARNING: carousel+shortcode json both missed, using raw <video> tag fallback")
    vid = _video_from_soup(html)
    if vid:
        return [vid]

    return []




def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    m = re.search(r'"username":"([^"]+)"', html)
    username = m.group(1) if m else "unknown_user"
    folder = os.path.join(output_dir, username)
    os.makedirs(folder, exist_ok=True)

    soup = BeautifulSoup(html, "html.parser")

    page_url_tag = soup.find("meta", property="og:url")   # <-- order-proof
    page_url = page_url_tag.get("content") if page_url_tag else None
    
    
    if not page_url:                                      # <-- new fallback
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
                page_url = canonical["href"]
                print(f"og:url missing, used canonical link instead: {page_url}")

    if not page_url:
        print(f"WARNING: no og:url or canonical found in {path}, yt-dlp fallback will be dead")

    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        content = meta.get("content", "")
        cm = re.search(r':\s*"(.*)"\.\s*$', content, re.DOTALL)
        if cm:
            with open(os.path.join(folder, "caption.txt"), "w", encoding="utf-8") as f:
                f.write(cm.group(1))
            print("Saved: caption.txt")

    media = get_post_media(html)
    print(f"{path}: found {len(media)} real post media item(s)")

    img_i = vid_i = 0
    saved_count = 0
    for url, is_video in media:
        if is_video and url.startswith("blob:"):
            vid_i += 1
            ok = _video_via_bs4_ytdlp(html, page_url, folder, vid_i)
            if ok:
                saved_count += 1
                print(f"Saved via yt-dlp: video_{vid_i}")
            else:
                print(f"Failed: {url} (blob, yt-dlp couldn't fetch)")
            continue

        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                if is_video:
                    vid_i += 1
                    fname = os.path.join(folder, f"video_{vid_i}.mp4")
                else:
                    img_i += 1
                    fname = os.path.join(folder, f"image_{img_i}.jpg")
                with open(fname, "wb") as f:
                    f.write(resp.content)
                print(f"Saved: {fname}")
                saved_count += 1
            else:
                print(f"Failed (status {resp.status_code}): {url}")
        except Exception as e:
            print(f"Failed: {url}\n{e}")

    if len(media) == 0:
        status = "failed"
    elif saved_count == len(media):
        status = "success"
    elif saved_count == 0:
        status = "failed"
    else:
        status = "partial"

    return username, status


if __name__ == "__main__":
    
    import pandas as pd

    log_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/Outputs"
    log_path = os.path.join(log_dir, "process_log.csv")

    files = [os.path.join(input_dir, file) for file in os.listdir(input_dir)]
    records = []

    for file in files:
        href_file_name = os.path.splitext(os.path.basename(file))[0]
        try:
            username, status = process_file(file)   # real status from download counts
        except Exception as e:
            print(f"Failed processing {href_file_name}: {e}")
            username, status = None, "failed"        # crash before any download = failed

        records.append({
            "href_file_name": href_file_name,
            "Folder_name": username,
            "Status": status
        })

    df = pd.DataFrame(records)
    df["_n"] = df["href_file_name"].str.extract(r"(\d+)").astype(int)
    df = df.sort_values("_n").drop(columns="_n")
    df.to_csv(log_path, index=False)          # <-- missing line, add back
    print(f"Log saved: {log_path}")
            
        # with open(file, "r", encoding="utf-8") as f:
        #     soup = BeautifulSoup(f.read(), "html.parser") 
        # process_file(file)
    
    # file = os.path(input_dir)
    # #files = sorted(os.path.join(input_dir, f) for f in os.listdir(input_dir))
    # for path in file:
    #     process_file(path)