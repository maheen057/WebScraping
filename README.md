# CodeAlpha Task 1 – Web Scraping and Data Collection using Python

A complete, beginner-friendly web scraping project built for the **CodeAlpha Data Analytics Internship**.
The project scrapes book information from **[books.toscrape.com](https://books.toscrape.com/)** — a public sandbox website created specifically for scraping practice — cleans the data, analyzes it and visualizes the results.

> ⚖️ **Ethics note:** books.toscrape.com is designed to be scraped and has no robots.txt restrictions. The scraper still uses a descriptive User-Agent, waits politely between requests, retries failures with backoff and never touches login-protected or private data.

---

## 📁 Project Structure

```
CodeAlpha_WebScraping/
├── main.py                          # Runs the whole pipeline end-to-end
├── requirements.txt                 # Python dependencies
├── README.md
├── data/
│   ├── scraped_data.csv             # Raw scraped dataset (~1000 records)
│   ├── cleaned_data.csv             # Cleaned dataset
│   ├── analysis_summary.txt         # Analysis report (averages, min/max, distributions)
│   └── category_summary.csv         # Category-wise statistics
├── src/
│   ├── scraper.py                   # Requests + BeautifulSoup scraping logic
│   ├── data_cleaning.py             # Missing values, duplicates, type conversion
│   ├── analysis.py                  # Statistical analysis
│   └── visualization.py             # Matplotlib charts
├── notebooks/
│   └── web_scraping_analysis.ipynb  # Jupyter Notebook walkthrough (with outputs)
└── assets/
    ├── price_distribution.png       # Histogram of prices
    ├── rating_distribution.png      # Bar chart of ratings
    ├── avg_price_by_category.png    # Category-wise comparison
    └── books_per_category.png       # Books per category
```

---

## 🚀 Getting Started (beginner friendly)

### 1. Install Python
You need **Python 3.9 or newer** from [python.org](https://www.python.org/downloads/).

### 2. Download / clone this project
```bash
git clone https://github.com/<your-username>/CodeAlpha_WebScraping.git
cd CodeAlpha_WebScraping
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the project
```bash
python main.py
```
The first run takes about **1–2 minutes** (it politely delays between requests). It will print progress, then save the dataset, the analysis summary and four charts.

### 5. Explore in Jupyter Notebook (optional)
```bash
jupyter notebook notebooks/web_scraping_analysis.ipynb
```
The notebook contains the full walkthrough with executed outputs — you can re-run every cell with **Cell → Run All**.

---

## 🧭 Complete Workflow (HTML → dataset → analysis)

1. **HTTP request** – `requests.Session` downloads each page (homepage first, then every category page and its paginated follow-ups).
2. **HTML parsing** – `BeautifulSoup(html, "html.parser")` turns the HTML into a searchable tree.
3. **Identifying tags & attributes** – each book lives in `<article class="product_pod">`; inside it:
   * `<h3><a title="...">` → book title
   * `<p class="price_color">` → price text like `£51.77`
   * `<p class="star-rating Three">` → rating encoded as a CSS class
   * `<p class="instock availability">` → availability text
   * category names come from the homepage sidebar `<div class="side_categories">`
4. **Pagination** – the scraper follows `<li class="next"><a href="page-2.html">` links until a category ends.
5. **Error handling** – timeouts, connection errors and HTTP errors are retried 3 times with backoff; failed pages are skipped, not crashed.
6. **Duplicate avoidance** – a `set` of product URLs guarantees each book appears once.
7. **Structured storage** – records go into a pandas DataFrame → `data/scraped_data.csv`.
8. **Data cleaning** – text whitespace cleanup, `£51.77` → `51.77` float, `"star-rating Three"` → `3`, `"In stock"` → boolean, rows with missing title/URL/price dropped, duplicates removed again defensively.
9. **Analysis** – totals, average/median/min/max price, rating frequency distribution, per-category statistics (all in `data/analysis_summary.txt`).
10. **Visualization** – four Matplotlib charts saved to `assets/`.

---

## 📊 Results snapshot

* **~1,000 unique books** across **~50 categories**
* Fields: `title`, `category`, `price`, `rating`, `in_stock`, `url`
* Full numbers are in [`data/analysis_summary.txt`](data/analysis_summary.txt); charts in [`assets/`](assets/).

| Chart | What it shows |
|---|---|
| `assets/price_distribution.png` | Histogram — how book prices spread |
| `assets/rating_distribution.png` | Bar chart — books per star rating |
| `assets/avg_price_by_category.png` | Category-wise average price comparison |
| `assets/books_per_category.png` | Number of books in the largest categories |

---

## 🛠️ Technologies

* **Python 3**
* `requests` – HTTP requests
* `BeautifulSoup4` – HTML parsing
* `pandas` – datasets and cleaning
* `matplotlib` – charts
* `Jupyter Notebook` – interactive walkthrough
* `CSV` – dataset storage

---

## 📝 Internship task checklist

- [x] Scrape a public, scraping-friendly website (respecting robots/limits)
- [x] HTTP requests, HTML parsing, tag/attribute identification
- [x] Pagination handling
- [x] Missing information & request error handling
- [x] Duplicate record avoidance
- [x] ≥100 records (≈1,000 collected)
- [x] CSV dataset with title, price, rating, availability, URL
- [x] Data cleaning (missing values, duplicates, type conversion, text & price cleaning)
- [x] Analysis (totals, averages, min/max, category-wise, frequency distribution)
- [x] Visualizations (bar, histogram, category comparisons, distribution)
- [x] Source code, datasets, analysis results, charts, notebook, README
