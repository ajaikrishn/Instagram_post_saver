#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 12:24:12 2026

@author: ajai-krishna
"""
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from html import unescape


input_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/Outputs/html_parsed_links"
output_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/Outputs/posts"




files = [os.path.join(input_dir,i) for i in os.listdir(input_dir)]
files.sort()
test = files[0]
print(test)
with open(test, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
html = str(soup)

width_pattern = re.compile(r'width:\s*(\d+)px')
src_pattern = re.compile(
    r'https://scontent[-\w]*\.cdninstagram\.com/v/t51\.82787-15/[^"?\s]+\.jpg\?[^"]+'
)

image_urls = set()
video_urls = set()

for tag in soup.find_all(style=True):
    m = width_pattern.search(tag.get("style", ""))
    if not m or int(m.group(1)) >= 479:
        continue
    candidates = [tag] + tag.find_all(["img", "video", "source"])
    for cand in candidates:
        for attr in ("src", "srcset"):
            val = cand.get(attr)
            if not val:
                continue
            for part in val.split(","):
                u = part.strip().split(" ")[0]
                if not u:
                    continue
                u = unescape(u.replace("\\/", "/"))
                if cand.name == "img":
                    if src_pattern.match(u):
                        image_urls.add(u)
                else:
                    video_urls.add(u)

is_reel = bool(video_urls)
urls = list(video_urls) if is_reel else list(image_urls)
ext = "mp4" if is_reel else "jpg"

match = re.search(r'"username":"([^"]+)"', html)
if match:
    username = match.group(1)

folder = os.path.join(output_dir, username)
os.makedirs(folder, exist_ok=True)

meta = soup.find("meta", attrs={"name": "description"})
if meta:
    content = meta["content"]
    m = re.search(r':\s*"(.*)"\.\s*$', content, re.DOTALL)
    if m:
        caption = m.group(1)
        with open(os.path.join(folder, "caption.txt"), "w", encoding="utf-8") as f:
            f.write(caption)
        print("Saved: caption.txt")

for i, url in enumerate(urls, start=1):
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        filename = os.path.join(folder, f"{'video' if is_reel else 'image'}_{i}.{ext}")
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Saved: {filename}")
    else:
        print(f"Failed to download {url}")

        
        
        
        