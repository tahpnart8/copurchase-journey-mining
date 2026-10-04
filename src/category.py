"""Assign product categories from co-purchase network communities."""

import collections
import itertools

import networkx as nx
import pandas as pd

from .config import LOUVAIN_RESOLUTION, LOUVAIN_SEED, MAX_BASKET_SIZE, MIN_CO_OCCURRENCE, MIN_LIFT, N_CATEGORIES


def build_co_purchase_graph(df: pd.DataFrame) -> nx.Graph:
    baskets = df.groupby("Invoice")["StockCode"].apply(lambda s: sorted(set(s)))

    pair_count: collections.Counter = collections.Counter()
    single_count: collections.Counter = collections.Counter()
    n_baskets = len(baskets)

    for items in baskets:
        single_count.update(items)
        if 1 < len(items) <= MAX_BASKET_SIZE:
            pair_count.update(itertools.combinations(items, 2))

    graph = nx.Graph()
    for (a, b), co in pair_count.items():
        if co < MIN_CO_OCCURRENCE:
            continue
        lift = (co / n_baskets) / ((single_count[a] / n_baskets) * (single_count[b] / n_baskets))
        if lift >= MIN_LIFT:
            graph.add_edge(a, b, weight=lift)

    return graph


def detect_communities(graph: nx.Graph) -> list[frozenset]:
    communities = nx.community.louvain_communities(
        graph, weight="weight", resolution=LOUVAIN_RESOLUTION, seed=LOUVAIN_SEED
    )
    return sorted(communities, key=len, reverse=True)


def assign_category(df: pd.DataFrame, communities: list[frozenset]) -> pd.Series:
    sku_to_category = {}
    for i, community in enumerate(communities[:N_CATEGORIES], start=1):
        for sku in community:
            sku_to_category[sku] = f"NET_{i}"
    return df["StockCode"].map(sku_to_category).fillna("OTHER")


def category_quality(df: pd.DataFrame, category_col: str) -> dict:
    """Coverage, median share of the top category per event, and rate of mixed events."""
    day = df["InvoiceDate"].dt.normalize()
    grouped = df.assign(Day=day).groupby(["CustomerID", "Day", category_col])["Revenue"].sum()
    top_per_event = grouped.groupby(level=[0, 1]).max()
    total_per_event = df.assign(Day=day).groupby(["CustomerID", "Day"])["Revenue"].sum()
    share = top_per_event / total_per_event

    return {
        "coverage": (df[category_col] != "OTHER").mean(),
        "median_share": share.median(),
        "mixed_basket_rate": (share < 0.4).mean(),
    }
