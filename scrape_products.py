from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# ---------------- CONFIG ----------------
CATEGORIES = {
    "phones": "https://www.lazada.com.my/catalog/?q=phone&page=",
    "home_appliances": "https://www.lazada.com.my/catalog/?q=home+appliances&page=",
    "fashion": "https://www.lazada.com.my/catalog/?q=fashion&page=",
    "beauty": "https://www.lazada.com.my/catalog/?q=beauty&page=",
    "toys": "https://www.lazada.com.my/catalog/?q=toys&page="
}

PAGES_PER_CATEGORY = 5
OUTPUT_FILE = "products_raw.csv"

# ---------------- DRIVER ----------------
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# ---------------- MANUAL CAPTCHA ----------------
driver.get("https://www.lazada.com.my/catalog/?q=phone&page=")
print("\n⚠️ Please solve the CAPTCHA manually in the browser ⚠️")
input("After CAPTCHA is completed and homepage loads, press ENTER here...")

products = []

# ---------------- SCRAPE ----------------
for category, base_url in CATEGORIES.items():
    print(f"\nScraping category: {category}")

    for page in range(1, PAGES_PER_CATEGORY + 1):
        url = base_url + str(page)
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.select("div[data-qa-locator='product-item']")
        print(f"Page {page}: found {len(items)} products")

        for item in items:
            try:
                # Product name (MOST RELIABLE)
                name_tag = item.select_one("a[title]")
                name = name_tag["title"].strip() if name_tag else None

                # Price
                price_text = item.select_one("span.ooOxS").get_text()
                price = float(re.sub(r"[^\d.]", "", price_text))

                # Sold quantity
                sold_text = item.get_text(" ")
                sold_match = re.search(r"(\d+)\s*sold", sold_text)
                sold = int(sold_match.group(1)) if sold_match else 0

                # Rating count
                rating_count_match = re.search(r"\((\d+)\)", sold_text)
                rating_count = int(rating_count_match.group(1)) if rating_count_match else 0

                # Rating
                rating_match = re.search(r"(\d\.\d)", sold_text)
                rating = float(rating_match.group(1)) if rating_match else None

                products.append({
                    "product_name": name,
                    "price": price,
                    "sold_quantity": sold,
                    "rating": rating,
                    "rating_count": rating_count,
                    "category": category
                })

            except Exception as e:
                print("Error:", e)
                continue

        time.sleep(2)

driver.quit()

df = pd.DataFrame(products)
print(f"\nTotal products scraped: {len(df)}")
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print("Saved to products_raw.csv")
