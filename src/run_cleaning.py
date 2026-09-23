"""Command-line entry point for the cleaning pipeline.

Usage:
    python -m src.run_cleaning data/raw/retail_store_sales.csv data/processed/clean.parquet
"""

import argparse
import logging

import pandas as pd

from src.cleaning import clean


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean the retail sales dataset.")
    parser.add_argument("input_csv", help="Path to the raw CSV file")
    parser.add_argument("output_parquet", help="Path for the cleaned parquet file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show the cleaning log")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    df = pd.read_csv(args.input_csv)
    df_clean = clean(df)
    df_clean.to_parquet(args.output_parquet)

    print(f"Cleaned {len(df_clean)} rows -> {args.output_parquet}")


if __name__ == "__main__":
    main()