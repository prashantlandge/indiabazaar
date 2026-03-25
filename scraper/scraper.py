"""
IndiaMart Scraper — requests-based

Scrapes supplier data from IndiaMart search results using their web interface.

Usage:
    python scraper.py --query "packaging material" --pages 5 --output results.json
    python scraper.py --query "hdpe pellets" --pages 3 --output hdpe.json
"""
import argparse
import json
import logging
import random
import re
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}


def scrape_search(query: str, max_pages: int = 5) -> list[dict]:
    """Scrape IndiaMart search results for a given query."""
    suppliers = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for page in range(1, max_pages + 1):
        logger.info(f"Scraping page {page}/{max_pages} for: {query}")

        try:
            # IndiaMart search URL pattern
            url = f"https://dir.indiamart.com/search.mp?ss={requests.utils.quote(query)}&src=as-rcnt"
            if page > 1:
                url += f"&page={page}"

            response = session.get(url, timeout=15)
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} for page {page}")
                continue

            soup = BeautifulSoup(response.text, "lxml")

            # Parse supplier cards from search results
            cards = soup.select(".suplr-card, .productsLst, .lstng, .card")
            if not cards:
                # Try alternative selectors
                cards = soup.select("[data-glid], .brs_lst, .productwrap")

            if not cards:
                logger.info(f"No results found on page {page}, trying alternative parsing")
                # Parse from any div with company info
                cards = soup.find_all("div", class_=re.compile(r"(card|listing|product|supplier)", re.I))

            for card in cards:
                supplier = _parse_supplier_card(card, soup)
                if supplier and supplier.get("company_name"):
                    suppliers.append(supplier)

            logger.info(f"Page {page}: found {len(cards)} cards, total suppliers: {len(suppliers)}")

            # Rate limiting
            time.sleep(random.uniform(2, 4))

        except requests.RequestException as e:
            logger.error(f"Request failed for page {page}: {e}")
            time.sleep(5)
            continue
        except Exception as e:
            logger.error(f"Parse error on page {page}: {e}")
            continue

    # Deduplicate by company name
    seen = set()
    unique = []
    for s in suppliers:
        key = s["company_name"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(s)

    logger.info(f"Total unique suppliers: {len(unique)}")
    return unique


def _parse_supplier_card(card, page_soup) -> dict | None:
    """Parse a single supplier card element into structured data."""
    try:
        supplier = {}

        # Company name
        name_el = card.select_one("a.lcname, .company-name, .cmpname, h2 a, h3 a, .cardhead a")
        if not name_el:
            name_el = card.select_one("a[title]")
        if name_el:
            supplier["company_name"] = name_el.get_text(strip=True)
            href = name_el.get("href", "")
            if href and "indiamart.com" in href:
                supplier["source_url"] = href
        else:
            return None

        if not supplier.get("company_name") or len(supplier["company_name"]) < 2:
            return None

        # Location
        loc_el = card.select_one(".loc, .location, .city-name, .addr, .lcity")
        if loc_el:
            location_text = loc_el.get_text(strip=True)
            parts = [p.strip() for p in location_text.split(",")]
            if parts:
                supplier["city"] = parts[0]
            if len(parts) > 1:
                supplier["state"] = parts[-1]

        # Rating
        rating_el = card.select_one(".rating, .star-rating, .rtn, [class*='rating']")
        if rating_el:
            rating_text = rating_el.get_text(strip=True)
            nums = re.findall(r"[\d.]+", rating_text)
            if nums:
                val = float(nums[0])
                if 0 < val <= 5:
                    supplier["rating"] = val

        # Verified badges
        if card.select_one(".verified, .trust-seal, [class*='verified'], [class*='trust']"):
            supplier["indiamart_verified"] = True
        if card.select_one("[class*='gst'], .gst-verified"):
            supplier["gst_verified"] = True

        # Nature of business
        biz_el = card.select_one(".nature, .nob, [class*='nature']")
        if biz_el:
            supplier["nature_of_business"] = biz_el.get_text(strip=True)

        # Products
        products = []
        product_els = card.select(".prd-name, .product-name, .pnm, li a")
        for pel in product_els[:10]:
            pname = pel.get_text(strip=True)
            if pname and len(pname) > 2 and len(pname) < 200:
                product = {"name": pname}
                # Try to find price near this element
                price_el = pel.find_next(class_=re.compile(r"price|prc"))
                if price_el:
                    product["price"] = price_el.get_text(strip=True)
                products.append(product)

        if products:
            supplier["products"] = products

        # Member since / year established
        year_el = card.select_one(".yr, .year, [class*='year'], [class*='member']")
        if year_el:
            year_text = year_el.get_text(strip=True)
            years = re.findall(r"(19|20)\d{2}", year_text)
            if years:
                supplier["year_established"] = int(years[0])

        # Number of employees
        emp_el = card.select_one("[class*='employee'], .emp")
        if emp_el:
            supplier["num_employees"] = emp_el.get_text(strip=True)

        # Certifications
        cert_els = card.select(".cert, .certification, [class*='cert']")
        certs = []
        for cel in cert_els:
            cert_text = cel.get_text(strip=True)
            if cert_text:
                certs.append(cert_text)
        if certs:
            supplier["certifications"] = certs

        # GST Number
        gst_el = card.select_one("[class*='gst']")
        if gst_el:
            gst_text = gst_el.get_text(strip=True)
            gst_match = re.search(r"\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z\d]{2}", gst_text)
            if gst_match:
                supplier["gst_number"] = gst_match.group()

        return supplier

    except Exception as e:
        logger.debug(f"Failed to parse card: {e}")
        return None


def scrape_supplier_profile(url: str, session: requests.Session = None) -> dict:
    """Scrape detailed supplier profile page for additional data."""
    if not session:
        session = requests.Session()
        session.headers.update(HEADERS)

    try:
        response = session.get(url, timeout=15)
        if response.status_code != 200:
            return {}

        soup = BeautifulSoup(response.text, "lxml")
        profile = {}

        # Contact person
        contact = soup.select_one(".cnt-nm, .contact-name, [class*='contact']")
        if contact:
            profile["contact_person"] = contact.get_text(strip=True)

        # Phone/Mobile
        phone = soup.select_one("[class*='phone'], [class*='mobile'], .phn")
        if phone:
            phone_text = phone.get_text(strip=True)
            digits = re.findall(r"\+?\d[\d\s-]{8,}", phone_text)
            if digits:
                profile["phone"] = digits[0].strip()

        # Email
        email = soup.select_one("[class*='email']")
        if email:
            email_text = email.get_text(strip=True)
            if "@" in email_text:
                profile["email"] = email_text

        # Address
        addr = soup.select_one(".address, .addr, [class*='address']")
        if addr:
            profile["address"] = addr.get_text(strip=True)

        # Website
        web = soup.select_one("a[href*='http'][class*='website'], a[href*='http'][class*='web']")
        if web:
            profile["website"] = web.get("href", "")

        # Annual turnover
        turn = soup.select_one("[class*='turnover']")
        if turn:
            profile["annual_turnover"] = turn.get_text(strip=True)

        # GST
        gst = soup.select_one("[class*='gst']")
        if gst:
            gst_text = gst.get_text(strip=True)
            gst_match = re.search(r"\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z\d]{2}", gst_text)
            if gst_match:
                profile["gst_number"] = gst_match.group()

        # Certifications from profile page
        cert_section = soup.select("[class*='cert'] li, [class*='cert'] span")
        certs = [c.get_text(strip=True) for c in cert_section if c.get_text(strip=True)]
        if certs:
            profile["certifications"] = certs

        return profile

    except Exception as e:
        logger.error(f"Profile scrape failed for {url}: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(description="IndiaMart Supplier Scraper")
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--pages", "-p", type=int, default=5, help="Number of pages to scrape")
    parser.add_argument("--output", "-o", default="results.json", help="Output file path")
    parser.add_argument("--detailed", "-d", action="store_true", help="Also scrape individual profiles")
    args = parser.parse_args()

    results = scrape_search(args.query, args.pages)

    if args.detailed and results:
        session = requests.Session()
        session.headers.update(HEADERS)
        for i, supplier in enumerate(results):
            if supplier.get("source_url"):
                logger.info(f"Scraping profile {i+1}/{len(results)}: {supplier['company_name']}")
                profile = scrape_supplier_profile(supplier["source_url"], session)
                supplier.update({k: v for k, v in profile.items() if v})
                time.sleep(random.uniform(1, 3))

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(results)} suppliers to {args.output}")


if __name__ == "__main__":
    main()
