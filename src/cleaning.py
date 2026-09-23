"""Cleaning functions for the retail store sales dataset."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def recover_missing_numerics(df: pd.DataFrame) -> pd.DataFrame:
    """Fill in Price Per Unit, Quantity, or Total Spent when the other two exist.

    Uses the exact relationship: Total Spent = Quantity * Price Per Unit.
    """
    df = df.copy()

    price, qty, total = "Price Per Unit", "Quantity", "Total Spent"

    # Recover each column from the other two
    mask = df[price].isna() & df[qty].notna() & df[total].notna()
    df.loc[mask, price] = df.loc[mask, total] / df.loc[mask, qty]
    logger.info("Recovered %d missing values in %s", mask.sum(), price)

    mask = df[qty].isna() & df[price].notna() & df[total].notna()
    df.loc[mask, qty] = df.loc[mask, total] / df.loc[mask, price]
    logger.info("Recovered %d missing values in %s", mask.sum(), qty)

    mask = df[total].isna() & df[price].notna() & df[qty].notna()
    df.loc[mask, total] = df.loc[mask, price] * df.loc[mask, qty]
    logger.info("Recovered %d missing values in %s", mask.sum(), total)

    return df

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
    keys = pd.MultiIndex.from_frame(df.loc[mask, ["Category", "Price Per Unit"]])
    df.loc[mask, "Item"] = lookup.reindex(keys).to_numpy()


    logger.info("Recovered %d missing values in %s", mask.sum(), "Item")

    return df