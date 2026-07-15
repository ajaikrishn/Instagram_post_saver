#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 10:46:33 2026

@author: ajai-krishna
"""

import os
from bs4 import BeautifulSoup

import sys

out_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links"

OUTPUT_FILE = os.path.join(out_dir, "post_links.txt")
BASE = "https://www.instagram.com"
# nav/chrome links that always show up (sidebar, header, etc) - not shared posts
SKIP = {
    "/", "#", "/explore/", "/reels/", "/direct/inbox/", "/direct/requests/",
}
SKIP_PREFIXES = ("/accounts/", "/data/")


def get_links(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()    
        if href in SKIP or href.startswith(SKIP_PREFIXES) or href.startswith("http"):
            continue
        if not href.startswith("/"):
            continue
    
        # keep post shares (/p/<code>/), reel shares (/reel/<code>/), profile shares (/username/)
        full = BASE + href
        links.add(full)
    return links
links = []


if __name__ =="__main__":
    loop = 2
    filename = os.path.join(out_dir, f"loop_{loop:03d}.txt")
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

if __name__ == "__main1__":
    for loop in range(51):
        filename = os.path.join(out_dir, f"loop_{loop:03d}.txt")
        links.append(list(get_links(filename)))
        
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for link in sorted(links):
            f.write(link + "\n")
    
    print(f"Saved {len(links)} links to {OUTPUT_FILE}")