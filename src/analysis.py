"""
Basic data analysis on the cleaned book dataset.

Produces a human-readable summary (data/analysis_summary.txt) plus a
per-category summary table (data/category_summary.csv).
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

PRICE_COL = "price"


def analyze_data(cleaned: pd.DataFrame) -> dict:
    """Compute all required statistics and return them as a dict."""
    results = {}

    # --- Total records -----------------------------------------------------
    results["total_records"] = len(cleaned)
    results["unique_titles"] = cleaned["title"].nunique()
    results["num_categories"] = cleaned["category"].nunique()

    # --- Numerical averages / min / max -------------------------------------
    price = cleaned[PRICE_COL]
    results["avg_price"] = round(price.mean(), 2)
    results["median_price"] = round(price.median(), 2)
    results["min_price"] = round(price.min(), 2)
    results["max_price"] = round(price.max(), 2)
    results["std_price"] = round(price.std(), 2)

    # --- Rating frequency distribution --------------------------------------
    results["rating_distribution"] = (
        cleaned["rating"].value_counts().sort_index().to_dict()
    )

    # --- Category-wise analysis ----------------------------------------------
    category_summary = (
        cleaned.groupby("category")
        .agg(
            books=("title", "count"),
            avg_price=(PRICE_COL, "mean"),
            min_price=(PRICE_COL, "min"),
            max_price=(PRICE_COL, "max"),
            avg_rating=("rating", "mean"),
        )
        .round(2)
        .sort_values("books", ascending=False)
        .reset_index()
    )
    results["category_summary"] = category_summary

    # --- Other interesting facts ----------------------------------------------
    top = category_summary.iloc[0]
    results["largest_category"] = (top["category"], int(top["books"]))
    most_expensive = cleaned.loc[cleaned[PRICE_COL].idxmax()]
    results["most_expensive_book"] = (most_expensive["title"], round(most_expensive[PRICE_COL], 2))
    cheapest = cleaned.loc[cleaned[PRICE_COL].idxmin()]
    results["cheapest_book"] = (cheapest["title"], round(cheapest[PRICE_COL], 2))
    results["in_stock_pct"] = round(100 * cleaned["in_stock"].mean(), 1)

    return results


def format_summary(results: dict) -> str:
    """Turn the results dict into a readable report."""
    dist = results["rating_distribution"]
    dist_lines = "\n".join(
        f"  {stars} star(s): {count} books" for stars, count in dist.items()
    )
    top5 = results["category_summary"].head(5).to_string(index=False)

    return f"""
=========================================================
 WEB SCRAPING PROJECT - DATA ANALYSIS SUMMARY
 Source: books.toscrape.com (public scraping sandbox)
=========================================================

1. DATASET OVERVIEW
   Total records collected : {results['total_records']}
   Unique book titles      : {results['unique_titles']}
   Categories              : {results['num_categories']}
   Books marked in stock   : {results['in_stock_pct']}%

2. PRICE STATISTICS
   Average price  : £{results['avg_price']}
   Median price   : £{results['median_price']}
   Minimum price  : £{results['min_price']}
   Maximum price  : £{results['max_price']}
   Std deviation  : £{results['std_price']}

3. RATING FREQUENCY DISTRIBUTION
{dist_lines}

4. CATEGORY-WISE ANALYSIS (top 5 categories by book count)
{top5}

5. NOTABLE FINDINGS
   Largest category    : {results['largest_category'][0]} ({results['largest_category'][1]} books)
   Most expensive book : "{results['most_expensive_book'][0]}" at £{results['most_expensive_book'][1]}
   Cheapest book       : "{results['cheapest_book'][0]}" at £{results['cheapest_book'][1]}

=========================================================
"""


def run(cleaned: pd.DataFrame) -> dict:
    """Run the analysis, save the summary and category table, return results."""
    results = analyze_data(cleaned)

    summary_path = DATA_DIR / "analysis_summary.txt"
    summary_path.write_text(format_summary(results), encoding="utf-8")

    category_path = DATA_DIR / "category_summary.csv"
    results["category_summary"].to_csv(category_path, index=False)

    print(format_summary(results))
    return results


if __name__ == "__main__":
    run(pd.read_csv(DATA_DIR / "cleaned_data.csv"))
