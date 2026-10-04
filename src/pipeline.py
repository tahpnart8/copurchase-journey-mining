"""Shared pipeline steps: locate raw file, cached cleaning, category assignment."""

import argparse
from pathlib import Path

import networkx as nx
import pandas as pd

from . import category, category_keyword, clean
from .config import OUTPUT_DIR, RAW_XLSX_CANDIDATES


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input", type=Path, help="path to online_retail_II.xlsx (auto-detected if omitted)")
    parser.add_argument("--outdir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def find_raw_xlsx(path: Path | None) -> Path:
    candidates = [path] if path else RAW_XLSX_CANDIDATES
    for candidate in candidates:
        if candidate.exists():
            return candidate
    searched = "\n  ".join(str(c) for c in candidates)
    raise SystemExit(f"online_retail_II.xlsx not found. Searched:\n  {searched}\n"
                     "Place it in data/ or pass --input <path>.")


def load_clean_cached(xlsx: Path, outdir: Path) -> tuple[pd.DataFrame, list[tuple[str, int]], int]:
    outdir.mkdir(parents=True, exist_ok=True)
    cache = outdir / "clean_base.pkl"
    if cache.exists():
        return pd.read_pickle(cache)
    raw = clean.load_raw(xlsx)
    df, audit = clean.clean(raw)
    result = (df, audit, len(raw))
    pd.to_pickle(result, cache)
    return result


def add_categories(df: pd.DataFrame, keyword: bool = False) -> tuple[pd.DataFrame, nx.Graph, list[frozenset]]:
    graph = category.build_co_purchase_graph(df)
    communities = category.detect_communities(graph)
    df = df.assign(Category=category.assign_category(df, communities))
    if keyword:
        df["CategoryKeyword"] = category_keyword.assign_category_keyword_series(df["Description"])
    return df, graph, communities
