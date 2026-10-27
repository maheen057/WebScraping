"""
Visualizations for the scraped book dataset using Matplotlib.

Creates four charts in assets/:
  1. price_distribution.png        - histogram of book prices
  2. rating_distribution.png       - bar chart of rating frequencies
  3. avg_price_by_category.png     - category-wise comparison (bar chart)
  4. books_per_category.png        - how many books each category holds
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # render to files; safe in scripts and notebooks
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"

# A consistent, simple style for every chart
plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "#fafafa",
        "axes.grid": True,
        "grid.color": "#dddddd",
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
    }
)

COLOR_MAIN = "#4472c4"
COLOR_ACCENT = "#c0504d"


def _save(fig, name: str) -> Path:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    path = ASSETS_DIR / name
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_price_distribution(cleaned: pd.DataFrame) -> Path:
    """Histogram: how book prices are spread."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.hist(cleaned["price"], bins=30, color=COLOR_MAIN, edgecolor="white")
    ax.set_title("Distribution of Book Prices", fontsize=14, fontweight="bold")
    ax.set_xlabel("Price (£)")
    ax.set_ylabel("Number of books")
    return _save(fig, "price_distribution.png")


def plot_rating_distribution(cleaned: pd.DataFrame) -> Path:
    """Bar chart: how many books have each star rating."""
    counts = cleaned["rating"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar([f"{int(r)}★" for r in counts.index], counts.values, color=COLOR_MAIN)
    ax.bar_label(bars, padding=3)
    ax.set_title("Book Ratings - Frequency Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Star rating")
    ax.set_ylabel("Number of books")
    return _save(fig, "rating_distribution.png")


def plot_avg_price_by_category(cleaned: pd.DataFrame, top_n: int = 12) -> Path:
    """Category-wise comparison: average price per category (top N by count)."""
    top = (
        cleaned.groupby("category")["price"].agg(["count", "mean"])
        .sort_values("count", ascending=False)
        .head(top_n)
        .sort_values("mean")
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(top.index, top["mean"], color=COLOR_MAIN)
    ax.bar_label(bars, fmt="£%.0f", padding=3)
    ax.set_title(f"Average Price by Category ({top_n} Largest Categories)",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Average price (£)")
    ax.set_ylabel("Category")
    ax.set_xlim(0, top["mean"].max() * 1.18)
    return _save(fig, "avg_price_by_category.png")


def plot_books_per_category(cleaned: pd.DataFrame, top_n: int = 12) -> Path:
    """Bar chart: number of books per category (top N)."""
    counts = cleaned["category"].value_counts().head(top_n).sort_values()
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(counts.index, counts.values, color=COLOR_ACCENT)
    ax.bar_label(bars, padding=3)
    ax.set_title(f"Books per Category (Top {top_n})", fontsize=14, fontweight="bold")
    ax.set_xlabel("Number of books")
    ax.set_ylabel("Category")
    ax.set_xlim(0, counts.max() * 1.15)
    return _save(fig, "books_per_category.png")


def create_all_charts(cleaned: pd.DataFrame) -> list[Path]:
    """Generate every chart and return the saved file paths."""
    paths = [
        plot_price_distribution(cleaned),
        plot_rating_distribution(cleaned),
        plot_avg_price_by_category(cleaned),
        plot_books_per_category(cleaned),
    ]
    for path in paths:
        print(f"Chart saved: {path}")
    return paths


if __name__ == "__main__":
    create_all_charts(pd.read_csv(PROJECT_ROOT / "data" / "cleaned_data.csv"))
