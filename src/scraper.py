"""
Web scraper for books.toscrape.com (a public sandbox site that permits
automated access for learning purposes).

Collects: Book Title, Category, Price, Rating, Availability, Product URL.
Handles pagination, request errors, retries, rate limiting and duplicates.

Author: CodeAlpha Internship - Task 1 (Web Scraping)
"""

import logging
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
BASE_URL = "https://books.toscrape.com/"
REQUEST_TIMEOUT = 20          # seconds per HTTP request
RETRIES = 3                   # retries per failed request
DELAY_RANGE = (0.5, 1.2)      # polite random delay between requests (seconds)
MAX_PAGES_PER_CATEGORY = 5    # safety cap for pagination

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

# Books To Scrape has no robots.txt restrictions and is explicitly built for
# scraping practice, but we still identify ourselves politely.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; CodeAlphaWebScrapingProject/1.0; "
        "+educational use)"
    )
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("scraper")

# Rating words used in the class attribute of <p class="star-rating Three">
RATING_WORDS = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
}


# --------------------------------------------------------------------------
# HTTP layer with error handling and retries
# --------------------------------------------------------------------------
def fetch_page(session: requests.Session, url: str) -> BeautifulSoup | None:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    for attempt in range(1, RETRIES + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as exc:
            logger.warning("Attempt %d/%d failed for %s: %s",
                           attempt, RETRIES, url, exc)
            time.sleep(2 * attempt)  # simple exponential backoff
    logger.error("Giving up on %s after %d attempts", url, RETRIES)
    return None


def polite_pause() -> None:
    """Random small delay so we never hammer the server."""
    time.sleep(DELAY_RANGE[0] + (DELAY_RANGE[1] - DELAY_RANGE[0]) * (int(time.time()) % 100) / 100)


# --------------------------------------------------------------------------
# HTML parsing helpers (identify tags and attributes explicitly)
# --------------------------------------------------------------------------
def parse_book_card(article, page_url: str) -> dict | None:
    """Extract one book record from an <article class="product_pod"> tag."""
    try:
        title_tag = article.select_one("h3 a")            # <h3><a title="...">
        link = title_tag.get("href") if title_tag else None
        if not title_tag or not link:
            return None  # cannot build a record without title + URL

        price_tag = article.select_one("p.price_color")    # <p class="price_color">£51.77
        rating_tag = article.select_one("p.star-rating")   # <p class="star-rating Three">
        avail_tag = article.select_one("p.instock.availability")

        return {
            "title": title_tag.get("title", "").strip(),
            "price_raw": price_tag.text.strip() if price_tag else None,
            "rating_raw": " ".join(rating_tag.get("class", [])) if rating_tag else None,
            "availability_raw": avail_tag.text.strip() if avail_tag else None,
            "product_url": urljoin(page_url, link),
        }
    except (AttributeError, KeyError) as exc:
        logger.debug("Skipping malformed card: %s", exc)
        return None


def get_category_links(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """
    Find category links in the homepage sidebar.

    HTML: <div class="side_categories"> <ul class="nav"> <li>
              <ul><li><a href="catalogue/category/books/travel_2/index.html">Travel (227)</a>
    """
    links = []
    sidebar = soup.select_one("div.side_categories")
    if sidebar is None:
        return links
    for a in sidebar.select("ul.nav li ul li a"):
        href = a.get("href")
        if not href:
            continue
        raw = a.text.strip()
        name = re.sub(r"\s*\(\d+\)\s*$", "", raw).strip()  # drop "(227)"
        links.append((name, urljoin(BASE_URL, href)))
    return links


# --------------------------------------------------------------------------
# Main scraping routine (handles pagination across category pages)
# --------------------------------------------------------------------------
def scrape_books() -> pd.DataFrame:
    """
    Scrape every category on books.toscrape.com.

    Request budget is small (1 homepage + ~50 category pages + paginated
    follow-ups) because we read category, price, rating and availability
    directly from the listing cards - we never visit all 1000 product pages.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    homepage = fetch_page(session, BASE_URL)
    if homepage is None:
        raise RuntimeError("Could not reach the homepage - check your connection.")

    categories = get_category_links(homepage)
    logger.info("Found %d categories on the homepage.", len(categories))

    records: list[dict] = []
    seen_urls: set[str] = set()

    for cat_number, (category, category_url) in enumerate(categories, start=1):
        page_url = category_url
        pages_visited = 0

        while page_url and pages_visited < MAX_PAGES_PER_CATEGORY:
            soup = fetch_page(session, page_url)
            if soup is None:
                break  # error already logged; move on to the next category

            for article in soup.select("article.product_pod"):
                record = parse_book_card(article, page_url)
                if record is None:
                    continue
                if record["product_url"] in seen_urls:
                    continue  # avoid duplicate records
                seen_urls.add(record["product_url"])
                record["category"] = category
                records.append(record)

            pages_visited += 1

            # Pagination: <li class="next"><a href="page-2.html">
            next_tag = soup.select_one("li.next a")
            page_url = urljoin(page_url, next_tag["href"]) if next_tag else None
            polite_pause()

        polite_pause()
        logger.info("[%d/%d] %-20s -> %d books so far (total)",
                    cat_number, len(categories), category, len(records))

    df = pd.DataFrame(
        records,
        columns=[
            "title", "category", "price_raw", "rating_raw",
            "availability_raw", "product_url",
        ],
    )
    logger.info("Scraping finished: %d unique book records collected.", len(df))
    return df


def run(force: bool = False) -> pd.DataFrame:
    """Run the scraper, or reuse data/scraped_data.csv when it already exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIR / "scraped_data.csv"
    if csv_path.exists() and not force:
        logger.info("Found existing %s - loading it (use run(force=True) to re-scrape).", csv_path.name)
        return pd.read_csv(csv_path)
    df = scrape_books()
    df.to_csv(csv_path, index=False)
    logger.info("Raw data saved to %s", csv_path)
    return df


if __name__ == "__main__":
    run(force=True)
