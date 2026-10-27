"""
CodeAlpha - Task 1: Web Scraping and Data Collection using Python
=================================================================

End-to-end pipeline:
  1. Scrape books from books.toscrape.com  ->  data/scraped_data.csv
  2. Clean the raw data                    ->  data/cleaned_data.csv
  3. Analyze the dataset                   ->  data/analysis_summary.txt
  4. Visualize the results                 ->  assets/*.png

Run from the project root:
    python main.py
"""

from src.analysis import run as run_analysis
from src.data_cleaning import run as run_cleaning
from src.scraper import run as run_scraper
from src.visualization import create_all_charts


def main() -> None:
    print("=" * 60)
    print("CodeAlpha Task 1 - Web Scraping and Data Collection")
    print("=" * 60)

    print("\nSTEP 1/4 - Scraping books.toscrape.com ...")
    raw_df = run_scraper()
    print(f"   Collected {len(raw_df)} unique records.")

    print("\nSTEP 2/4 - Cleaning the dataset ...")
    cleaned_df = run_cleaning()
    print(f"   Cleaned dataset: {len(cleaned_df)} rows x {len(cleaned_df.columns)} columns.")

    print("\nSTEP 3/4 - Analyzing the dataset ...")
    run_analysis(cleaned_df)
    print("   Summary written to data/analysis_summary.txt")

    print("\nSTEP 4/4 - Creating charts ...")
    create_all_charts(cleaned_df)

    print("\nDone! Outputs:")
    print("   data/scraped_data.csv      - raw scraped dataset")
    print("   data/cleaned_data.csv      - cleaned dataset")
    print("   data/analysis_summary.txt  - analysis report")
    print("   data/category_summary.csv  - category-wise statistics")
    print("   assets/*.png               - charts")


if __name__ == "__main__":
    main()
