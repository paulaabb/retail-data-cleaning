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