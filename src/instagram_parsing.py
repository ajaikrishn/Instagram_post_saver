#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------
out_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links"
BROWSER = "/usr/local/bin/geckodriver"
fetch_link = "https://www.instagram.com/direct/t/116177586439207/"

os.makedirs(out_dir, exist_ok=True)


options = Options()
options.binary_location = BROWSER
driver = webdriver.Firefox(options=options)

try:
    print("Waiting for login...")
    WebDriverWait(driver, 300).until(EC.invisibility_of_element_located((By.XPATH, "//input[@name='password']")))
    print("Login detected.")
    driver.get(fetch_link)
    
    print("Login to Instagram if required.")
    input("After the DM chat is completely loaded, press ENTER...")

    '''    
    # Locate the chat scroll container
    scroll_box = driver.find_element(
        By.XPATH,
        "//div[@role='main']//div[contains(@style,'overflow')]"
    )
    '''
    # Save first HTML
    html = driver.page_source
    with open(os.path.join(out_dir, "loop_000.txt"), "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved loop_000.txt")
    current = 0
    step = -500

    for loop in range(1, 51):      # 50 scrolls
        current += step
        '''
        driver.execute_script(
            "arguments[0].scrollTop = arguments[1];",
            scroll_box,
            current
        )
        '''
        driver.execute_script("window.scrollBy(0, -500);") 
        time.sleep(5)

        html = driver.page_source

        filename = os.path.join(out_dir, f"loop_{loop:03d}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved {filename}")

    print("Finished.")

    input("Press ENTER to close...")

finally:
    driver.quit()