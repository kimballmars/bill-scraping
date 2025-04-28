# -------------------------------------------------
# pip install selenium beautifulsoup4 webdriver-manager

import json                        
import re                           
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

URL = "https://iga.in.gov/legislative/2025/bills/senate/1/details"


def scrape_bill(url: str, wait_time: int = 30) -> dict:
    """
    Grab bill header, sponsors, full digest, and latest-action table,
    return them in a tiny JSON-ready dict.
    """
    opts = webdriver.ChromeOptions()
    opts.add_argument("--start-maximized")            
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                           options=opts)

    try:
        driver.get(url)

        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div[class^='BillDetails_digest'], "
                "table[class^='Table_tableDefaults']"))
        )

        # click “View more” if the digest is truncated
        try:
            btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    # match either label, even if nested inside a <span>
                    "//div[starts-with(@class,'BillDetails_digest')]"
                    "//button[.//*[contains(normalize-space(.),'View more')] "
                    "       or contains(normalize-space(.),'View more')]"
                ))
            )

            # scroll it into view *before* clicking
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)   # JS click is more reliable

            # wait until the button *text* flips to "Show less"
            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element((By.XPATH, "//*[self::button or self::span]"),
                                                  "Show less")
            )
        except TimeoutException:
            # no button → digest was already fully visible
            pass


        soup = BeautifulSoup(driver.page_source, "html.parser")
        for t in soup(["script", "style"]):
            t.decompose()

        # final payload
        out = {}                   

        # ---- title line ----
        header = soup.select_one("div[class^='BillDetails_header'] h1")
        if header:
            out["title"] = header.get_text(strip=True)

        # ---- sponsors ----
        info = soup.select_one("div[class^='BillDetails_billInfo']")
        sponsors_raw = ""
        if info:
            info_text = info.get_text(" ", strip=True)
            m = re.search(
                r"(?:Authored by|Sponsored by|Co-Authored by):\s*(.*?)\s*(?:Digest|$)",
                info_text, flags=re.S)
            if m:
                sponsors_raw = m.group(1)
        out["sponsors"] = [s.strip(" ,.") for s in sponsors_raw.split(",") if s.strip()]

        # ---- digest ----
        digest = soup.select_one("div[class^='BillDetails_digest']")
        if digest:
            out["digest"] = digest.get_text(" ", strip=True)

        # ---- latest-actions table ----
        table = soup.select_one("table[class^='Table_tableDefaults']")
        if table:
            out["actions"] = table.get_text(" ", strip=True)

        out["source"] = url          
        return out

    finally:
        driver.quit()


# ---------------- demo -----------------
if __name__ == "__main__":
    bill_json = scrape_bill(URL)

    # pretty-print the single-bill JSON 
    print(json.dumps(bill_json, indent=2, ensure_ascii=False))

