#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 15:04:41 2026

@author: ajai-krishna
"""

import os
import pandas as pd

link_file = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links/links.txt"

with open(link_file, "r") as file:
    links = file.read().splitlines()

reel_links = [link for link in links if "/reel/" in link]

print(reel_links)