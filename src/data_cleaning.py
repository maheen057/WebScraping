"""
Data cleaning for the scraped book dataset.

Steps: text cleaning, price extraction to float, rating conversion to int,
boolean availability, missing-value handling and duplicate removal.
"""

import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("cleaning")

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def clean_text(value) -> str:
    """Collapse whitespace and strip a text value; '' when missing."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def extract_price(value) -> float:
    """'£51.77' -> 51.77. Handles any currency symbol / stray text."""
    if value is None:
        return np.nan
    match = re.search(r"[\d.,]+", str(value))
    if not match:
        return np.nan
    text = match.group().replace(",", "")
    try:
        return round(float(text), 2)
    except ValueError:
        return np.nan


def extract_rating(value) -> int:
    """'star-rating Three' -> 3; 0 when the rating is missing/unknown."""
    if value is None:
        return 0
    for word, number in RATING_MAP.items():
        if word in str(value):
            return number
    return 0


def is_in_stock(value) -> bool:
    """'In stock' -> True, anything else -> False."""
    return "in stock" in str(value or "").lower()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the raw scraped data."""
    cleaned = df.copy()
    initial_rows = len(cleaned)

    # 1. Text cleaning
    cleaned["title"] = cleaned["title"].map(clean_text)
    cleaned["category"] = cleaned["category"].map(clean_text)
    cleaned["category"] = cleaned["category"].replace("", "Uncategorised")

    # 2. Data type conversion / numerical extraction
    cleaned["price"] = cleaned["price_raw"].map(extract_price)
    cleaned["rating"] = cleaned["rating_raw"].map(extract_rating).astype(int)
    cleaned["in_stock"] = cleaned["availability_raw"].map(is_in_stock).astype(bool)

    # 3. Missing value handling
    #    A record is only useful when it has a title, URL and a price.
    missing = cleaned["title"].eq("") | cleaned["product_url"].isna() | cleaned["price"].isna()
    cleaned = cleaned[~missing].copy()

    # 4. Duplicate removal (by product URL and also by title+category)
    before_dedupe = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["product_url"]).copy()
    cleaned = cleaned.drop_duplicates(subset=["title", "category"]).copy()

    # 5. Final, well-named columns
    cleaned = cleaned.rename(columns={"product_url": "url"})
    cleaned = cleaned[["title", "category", "price", "rating", "in_stock", "url"]].reset_index(drop=True)

    logger.info(
        "Cleaning summary: %d raw rows -> %d kept (%d malformed/missing dropped, "
        "%d duplicates removed)",
        initial_rows, len(cleaned), int(missing.sum()), before_dedupe - len(cleaned),
    )
    return cleaned


def run() -> pd.DataFrame:
    """Load scraped_data.csv, clean it and save cleaned_data.csv."""
    raw = pd.read_csv(DATA_DIR / "scraped_data.csv")
    cleaned = clean_data(raw)
    out_path = DATA_DIR / "cleaned_data.csv"
    cleaned.to_csv(out_path, index=False)
    logger.info("Cleaned data saved to %s", out_path)
    return cleaned


if __name__ == "__main__":
    run()
