"""Load and clean the Online Retail II dataset."""

from pathlib import Path

import pandas as pd

from .config import SERVICE_CODES


def load_raw(path: Path) -> pd.DataFrame:
    # Do not tag rows by sheet: the sheets overlap by 9 days and tagging breaks dedup.
    sheets = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    df = pd.concat(sheets.values(), ignore_index=True)
    df["Invoice"] = df["Invoice"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    return df


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[tuple[str, int]]]:
    audit = []
    df = raw.copy()

    n = len(df)
    df = df[~df["Invoice"].str.startswith("C")]
    audit.append(("cancelled_invoices", n - len(df)))

    n = len(df)
    df = df[df["Customer ID"].notna()]
    audit.append(("missing_customer_id", n - len(df)))

    n = len(df)
    df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]
    audit.append(("non_positive_quantity_or_price", n - len(df)))

    n = len(df)
    df = df[~df["StockCode"].isin(SERVICE_CODES)]
    audit.append(("service_or_fee_codes", n - len(df)))

    n = len(df)
    df = df.drop_duplicates()
    audit.append(("exact_duplicates", n - len(df)))

    df = df.rename(columns={"Customer ID": "CustomerID"})
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["Revenue"] = df["Quantity"] * df["Price"]

    return df.reset_index(drop=True), audit


def print_audit(n_raw: int, audit: list[tuple[str, int]], n_final: int) -> None:
    print(f"raw rows: {n_raw:,}")
    for step, removed in audit:
        print(f"  {step}: -{removed:,}")
    print(f"remaining: {n_final:,} ({n_final / n_raw:.1%})")
