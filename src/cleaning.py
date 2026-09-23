"""Cleaning functions for the retail store sales dataset."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def recover_items(df: pd.DataFrame) -> pd.DataFrame:
    """Recover missing Item values from Category + Price Per Unit.

    Exploration showed each (Category, Price Per Unit) pair maps to
    exactly one Item, so this lookup is deterministic.
    """
    df = df.copy()

    # Build the lookup table from rows where Item is known
    lookup = (
        df.dropna(subset=["Item"])
        .drop_duplicates(subset=["Category", "Price Per Unit"])
        .set_index(["Category", "Price Per Unit"])["Item"]
    )

    
    #         but Category and Price Per Unit are present
    mask = df["Item"].isna() & df["Category"].notna() & df["Price Per Unit"].notna()

    # Look up the item for those rows
    if mask.any():
        keys = pd.MultiIndex.from_frame(df.loc[mask, ["Category", "Price Per Unit"]])
        df.loc[mask, "Item"] = lookup.reindex(keys).to_numpy()

    logger.info("Recovered %d missing values in %s", mask.sum(), "Item")

    return df

def convert_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the Transaction Date column to datetime.

    Unparseable dates become NaT; the count is logged as a check.
    """
    df = df.copy()
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], errors="coerce")
    n_bad = df["Transaction Date"].isna().sum()
    logger.info("Converted Transaction Date to datetime (%d unparseable)", n_bad)
    return df

def clean_discount(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Discount Applied to a nullable boolean.

    ~4,200 rows (33%) are missing. We keep them as NA rather than
    imputing: there is no basis to guess, and filling with False
    would fabricate data. Analyses must handle NA explicitly.
    """
    df = df.copy()
    df["Discount Applied"] = df["Discount Applied"].astype("boolean")
    logger.info("Converted Discount Applied to nullable boolean (%d NA kept)",
                df["Discount Applied"].isna().sum())
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full cleaning pipeline on the raw dataset."""
    logger.info("Starting cleaning pipeline: %d rows, %d columns", *df.shape)
    df = recover_missing_numerics(df)
    df = recover_items(df)
    df = convert_dates(df)
    df = clean_discount(df)
    logger.info("Pipeline finished: %d values still missing", df.isna().sum().sum())
    return df

def recover_missing_numerics(df: pd.DataFrame) -> pd.DataFrame:
    """Fill in Price Per Unit, Quantity, or Total Spent when the other two exist.

    Uses the exact relationship: Total Spent = Quantity * Price Per Unit.
    """
    df = df.copy()

    price, qty, total = "Price Per Unit", "Quantity", "Total Spent"

    mask = df[price].isna() & df[qty].notna() & df[total].notna()
    if mask.any():
        df.loc[mask, price] = df.loc[mask, total] / df.loc[mask, qty]
    logger.info("Recovered %d missing values in %s", mask.sum(), price)

    mask = df[qty].isna() & df[price].notna() & df[total].notna()
    if mask.any():
        df.loc[mask, qty] = df.loc[mask, total] / df.loc[mask, price]
    logger.info("Recovered %d missing values in %s", mask.sum(), qty)

    mask = df[total].isna() & df[price].notna() & df[qty].notna()
    if mask.any():
        df.loc[mask, total] = df.loc[mask, price] * df.loc[mask, qty]
    logger.info("Recovered %d missing values in %s", mask.sum(), total)

    return df