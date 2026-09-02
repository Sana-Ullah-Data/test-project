"""
Entry point. Replaces the manual weekly Excel routine.

    python run_pipeline.py

Reads the raw export, cleans it, answers the four standing questions,
writes tidy CSVs and four charts into outputs/.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import analyse, clean, report

DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")


def main() -> None:
    raw = pd.read_csv(DATA_DIR / "sales_raw.csv")
    stock = pd.read_csv(DATA_DIR / "stock_reference.csv")

    sales = clean.clean_sales(raw)

    dropped = len(raw) - len(sales)
    print(f"Loaded {len(raw)} raw rows.")
    print(f"Cleaned to {len(sales)} usable invoice lines ({dropped} removed).")
    print(f"Period: {sales.date.min():%d %b %Y} to {sales.date.max():%d %b %Y}")
    print(f"Net revenue: PKR {sales.net_pkr.sum():,.0f}\n")

    monthly = analyse.monthly_revenue(sales)
    products = analyse.revenue_by_product(sales)
    clients = analyse.revenue_by_client(sales)
    dormant = analyse.dormant_clients(sales, days=45)
    reorder = analyse.reorder_report(sales, stock)
    seasonal = analyse.category_by_month(sales)

    OUTPUT_DIR.mkdir(exist_ok=True)
    monthly.to_csv(OUTPUT_DIR / "monthly_revenue.csv", index=False)
    products.to_csv(OUTPUT_DIR / "revenue_by_product.csv", index=False)
    clients.to_csv(OUTPUT_DIR / "revenue_by_client.csv", index=False)
    dormant.to_csv(OUTPUT_DIR / "dormant_clients.csv", index=False)
    reorder.to_csv(OUTPUT_DIR / "reorder_report.csv", index=False)
    seasonal.to_csv(OUTPUT_DIR / "category_by_month.csv")

    report.plot_monthly_revenue(monthly)
    report.plot_pareto(products)
    report.plot_days_of_cover(reorder)
    report.plot_category_heat(seasonal)

    top = products.head(3)
    print("Top three products by revenue:")
    for _, row in top.iterrows():
        print(f"  {row['product_name']:<32} PKR {row['net_pkr']:>12,.0f}  ({row['share_pct']}%)")

    n_reorder = int(reorder.reorder_now.sum())
    print(f"\n{n_reorder} products need reordering before stock runs out.")
    print(f"{len(dormant)} clients have not ordered in 45 days.")
    print(f"\nWritten to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
