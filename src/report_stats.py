"""Descriptive statistics used to populate the EDA report."""

import pandas as pd


def purchase_frequency(df: pd.DataFrame) -> pd.Series:
    return df.groupby("CustomerID")["Invoice"].nunique()


def order_value(df: pd.DataFrame) -> pd.Series:
    return df.groupby("Invoice")["Revenue"].sum()


def customer_lifetime_days(df: pd.DataFrame) -> pd.Series:
    per_customer = df.groupby("CustomerID")["InvoiceDate"].agg(["min", "max"])
    return (per_customer["max"] - per_customer["min"]).dt.days


def inter_purchase_gap_days(df: pd.DataFrame) -> pd.Series:
    invoice_dates = df.groupby(["CustomerID", "Invoice"])["InvoiceDate"].min().reset_index()
    invoice_dates = invoice_dates.sort_values(["CustomerID", "InvoiceDate"])
    return invoice_dates.groupby("CustomerID")["InvoiceDate"].diff().dt.days


def basket_size(df: pd.DataFrame) -> pd.Series:
    return df.groupby("Invoice")["StockCode"].nunique()


def product_revenue_concentration(df: pd.DataFrame, top_n: int) -> float:
    by_sku = df.groupby("StockCode")["Revenue"].sum().sort_values(ascending=False)
    return by_sku.head(top_n).sum() / by_sku.sum()


def monthly_revenue(df: pd.DataFrame) -> pd.Series:
    return df.set_index("InvoiceDate").resample("ME")["Revenue"].sum()


def period_split(df: pd.DataFrame, cutoff: str) -> dict:
    period1 = set(df.loc[df["InvoiceDate"] < cutoff, "CustomerID"])
    period2 = set(df.loc[df["InvoiceDate"] >= cutoff, "CustomerID"])
    return {
        "period1_customers": len(period1),
        "period2_customers": len(period2),
        "overlap_customers": len(period1 & period2),
    }
