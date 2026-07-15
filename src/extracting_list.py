
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
link_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links"
links = []
output_file = os.path.join(link_dir, "links.txt")
BROWSER = "/usr/local/bin/geckodriver"

#scroll in loop 0 to -500
#in each loop get page sour

options = Options()
options.binary_location = BROWSER

driver = webdriver.Firefox(options=options)

#driver.get("https://www.instagram.com")
driver = webdriver.Firefox(options=options)
links = set()
 
try:
    print("Waiting for login...")
    WebDriverWait(driver, 300).until(EC.invisibility_of_element_located((By.XPATH, "//input[@name='password']")))
    print("Login detected.")
    driver.get("https://www.instagram.com/direct/t/116177586439207/")
    input("Log in if needed, open thread, then press Enter to start scraping...")
 
    last_height = None
    scroll_box = driver.find_element("xpath", "//div[@role='grid'] | //body")
 
    while True:
        # parse current DOM for links
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http"):
                links.add(href)
            elif href.startswith("/"):
                links.add("https://www.instagram.com" + href)
                
        current = driver.execute_script("return arguments[0].scrollTop", scroll_box)
        step = driver.execute_script("return arguments[0].clientHeight", scroll_box)
        target = max(0, current - step)
 
        driver.execute_script("arguments[0].scrollTop = 0", scroll_box)  # scroll toward top (older msgs)
        time.sleep(2)
 
        new_height = driver.execute_script("return arguments[0].scrollTop", scroll_box)
        if last_height is not None and new_height == last_height:
            break  # reached top, no more history
        last_height = new_height
 
finally:
    with open(output_file, "w", encoding="utf-8") as f:
        for link in sorted(links):
            f.write(link + "\n")
    print(f"Saved {len(links)} links to {output_file}")
    input("Press Enter to close...")
    driver.quit()



with open(output_file, "w", encoding="utf-8") as f:
    for link in links:
        f.write(link + "\n")

print(f"Saved {len(links)} links to {output_file}")

input("Press Enter to close...")


driver.quit()