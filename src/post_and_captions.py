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
import 
from bs4 import BeautifulSoup
from html import unescape


input_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/Outputs/html_parsed_links"
output_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/Outputs/posts"


files = [os.path.join(input_dir,i) for i in os.listdir(input_dir)]
files.sort()
print(files)
test = [i for i in files if i.endswith('links_9.txt')]
print(test)
test = test[0]                    # <-- unwrap list -> single path
with open(test, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
html = str(soup)


target_class = "xvbhtw8 x78zum5 xdt5ytf x1iyjqo2 xl56j7k"

post = soup.find(class_=target_class.split())

if post:
    urls = set()

    for tag in post.find_all(["img", "video"]):
        src = tag.get("src")
        if src:
            urls.add(unescape(src.replace("\\/", "/")))

        srcset = tag.get("srcset")
        if srcset:
            for part in srcset.split(","):
                urls.add(unescape(part.strip().split(" ")[0].replace("\\/", "/")))
urls_lists  = list(urls)

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
            print(f"Saved: caption.txt")

is_reel = "/reel/" in test

if is_reel:
#    urls = re.findall(r'https:\\/\\/[^"]+\.mp4\?[^"]+', html)
#    urls = [unescape(u.replace("\\/", "/")) for u in urls ]
    urls = list(dict.fromkeys(urls_lists))
    ext = "mp4"
else:
#    urls = re.findall(r'https:\\/\\/scontent[-\w]*\.cdninstagram\.com[^"]+', html)
#    urls = [unescape(u.replace("\\/", "/")) for u in urls]
#    urls = [u for u in urls if "t51.82787-15" in u and "150x150" not in u]
#    urls = [u for u in urls if u not in urls]
    urls = list(dict.fromkeys(urls_lists))
    ext = "jpg"
for i, url in enumerate(urls, start=1):
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            filename = os.path.join(folder, f"{'video' if is_reel else 'image'}_{i}.{ext}")
            with open(filename, "wb") as f:
                f.write(response.content)
                print(f"Saved: {filename}")
    except Exception as e:
            print(f"Failed: {url}")
            print(e)