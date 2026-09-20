"""Merge same-day invoices into purchase events and build customer sequences."""

import numpy as np
import pandas as pd

from .config import MIN_CELL_OBSERVATIONS, MIN_SEQUENCE_LENGTH


def build_purchase_events(df: pd.DataFrame, category_col: str) -> pd.DataFrame:
    day = df["InvoiceDate"].dt.normalize()
    work = df.assign(Day=day)

    events = (
        work.groupby(["CustomerID", "Day"])
        .agg(Revenue=("Revenue", "sum"), NumSKU=("StockCode", "nunique"))
        .reset_index()
    )

    by_category = work.groupby(["CustomerID", "Day", category_col])["Revenue"].sum().reset_index()
    top_idx = by_category.groupby(["CustomerID", "Day"])["Revenue"].idxmax()
    top_category = by_category.loc[top_idx].rename(columns={"Revenue": "TopRevenue"})

    events = events.merge(top_category[["CustomerID", "Day", category_col, "TopRevenue"]],
                           on=["CustomerID", "Day"])
    events["Share"] = events["TopRevenue"] / events["Revenue"]
    events = events.sort_values(["CustomerID", "Day"]).reset_index(drop=True)
    events["Order"] = events.groupby("CustomerID").cumcount() + 1

    return events


def eligible_customers(events: pd.DataFrame, min_length: int = MIN_SEQUENCE_LENGTH) -> pd.Index:
    counts = events.groupby("CustomerID").size()
    return counts[counts >= min_length].index


def transition_matrix(events: pd.DataFrame, category_col: str, min_length: int = MIN_SEQUENCE_LENGTH):
    keep = eligible_customers(events, min_length)
    seq = events[events["CustomerID"].isin(keep)].copy()
    seq["Next"] = seq.groupby("CustomerID")[category_col].shift(-1)
    transitions = seq.dropna(subset=["Next"])

    counts = pd.crosstab(transitions[category_col], transitions["Next"])
    probs = counts.div(counts.sum(axis=1), axis=0)
    reliable = counts >= MIN_CELL_OBSERVATIONS

    return counts, probs, reliable


def self_transition_rate(counts: pd.DataFrame) -> float:
    return np.trace(counts.values) / counts.values.sum()
