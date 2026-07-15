from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------
links_dir = "/home/ajai-krishna/Documents/Instagram_posts_climate-change/links"
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