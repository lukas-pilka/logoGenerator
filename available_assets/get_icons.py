import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path

# https://chromedriver.chromium.org/downloads
# xattr -d com.apple.quarantine chromedriver 

base = Path(__file__).parent
url = "https://www.iconfinder.com/search/?q=car&price=free"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# driver = webdriver.Chrome(base/"chromedriver")
# driver.get(url)
# soup = BeautifulSoup(driver.page_source, "html.parser")

# with open(base/"output.html", "w+") as output_file:
#     output_file.write(str(soup.prettify()))
# driver.close()

icons = soup.select("a.d-block")
for icon in icons:
    icon_url = f"icons/{Path(icon['href']).parent.stem}/download/svg/512"
    try:
        response = requests.get(f"https://www.iconfinder.com/{icon_url}")
        print(f"https://www.iconfinder.com/{icon_url}")
        # print(response.text)
    except:
        print("failed")
    
