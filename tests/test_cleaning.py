"""Tests for the cleaning pipeline."""

from src.cleaning import recover_missing_numerics, recover_items

import pandas as pd


def test_recovers_missing_price():
    df = pd.DataFrame({
        "Price Per Unit": [None, 10.0],
        "Quantity":       [4.0,  2.0],
        "Total Spent":    [20.0, 20.0],
    })
    result = recover_missing_numerics(df)
    assert result["Price Per Unit"].iloc[0] == 5.0          # 20 / 4
    assert result["Price Per Unit"].isna().sum() == 0


def test_does_not_modify_input():
    df = pd.DataFrame({
        "Price Per Unit": [None],
        "Quantity":       [4.0],
        "Total Spent":    [20.0],
    })
    recover_missing_numerics(df)
    assert df["Price Per Unit"].isna().sum() == 1


def test_recovers_item_from_category_and_price():
    df = pd.DataFrame({
        "Category":       ["Food", "Food", "Food"],
        "Price Per Unit": [5.0,    5.0,    5.0],
        "Item":           ["Apple", "Apple", None],
    })
    result = recover_items(df)
    assert result["Item"].iloc[2] == "Apple"


def test_leaves_unrecoverable_item_missing():
    df = pd.DataFrame({
        "Category":       ["Food"],
        "Price Per Unit": [None],
        "Item":           [None],
    })
    result = recover_items(df)
    assert result["Item"].isna().all()      # nothing invented

from src.cleaning import (
    recover_missing_numerics,
    recover_items,
    convert_dates,
    clean_discount,
    clean,
)

def test_converts_dates_and_coerces_bad_ones():
    df = pd.DataFrame({
        "Transaction Date": ["2024-01-15", "not a date"],
    })
    result = convert_dates(df)
    assert pd.api.types.is_datetime64_any_dtype(result["Transaction Date"])
    assert result["Transaction Date"].isna().sum() == 1     # the bad one became NaT

def test_discount_becomes_boolean_and_keeps_na():
    df = pd.DataFrame({
        "Discount Applied": [True, False, None],
    })
    result = clean_discount(df)
    assert result["Discount Applied"].dtype == "boolean"
    assert result["Discount Applied"].isna().sum() == 1     # NA preserved, not filled

def test_full_pipeline_end_to_end():
    df = pd.DataFrame({
        "Transaction ID":   ["T1", "T2"],
        "Customer ID":      ["C1", "C2"],
        "Category":         ["Food", "Food"],
        "Item":             ["Apple", None],        # row 2: recoverable via lookup
        "Price Per Unit":   [5.0, 5.0],
        "Quantity":         [2.0, 3.0],
        "Total Spent":      [None, 15.0],           # row 1: recoverable via equation
        "Payment Method":   ["Cash", "Cash"],
        "Location":         ["Online", "In-store"],
        "Transaction Date": ["2024-01-15", "2024-02-20"],
        "Discount Applied": [True, None],
    })

    result = clean(df)

    # equation-based recovery: 2 * 5.0
    assert result["Total Spent"].iloc[0] == 10.0

    # lookup-based recovery: (Food, 5.0) -> Apple
    assert result["Item"].iloc[1] == "Apple"

    # types survived the full pipeline
    assert pd.api.types.is_datetime64_any_dtype(result["Transaction Date"])
    assert result["Discount Applied"].dtype == "boolean"

    # nothing was fabricated: row 2's unknown discount stays unknown
    assert result["Discount Applied"].isna().sum() == 1