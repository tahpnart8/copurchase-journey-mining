"""Run the full pipeline: raw data -> clean -> category -> sequences.

Usage:
    python scripts/run_pipeline.py --input data/online_retail_II.xlsx --outdir outputs
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import category, clean, sequence  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--outdir", default="outputs")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    raw = clean.load_raw(Path(args.input))
    df, audit = clean.clean(raw)
    clean.print_audit(len(raw), audit, len(df))

    graph = category.build_co_purchase_graph(df)
    communities = category.detect_communities(graph)
    df["Category"] = category.assign_category(df, communities)

    quality = category.category_quality(df, "Category")
    print(f"\ncoverage: {quality['coverage']:.1%}")
    print(f"median dominant-category share: {quality['median_share']:.3f}")
    print(f"mixed-basket rate: {quality['mixed_basket_rate']:.1%}")

    events = sequence.build_purchase_events(df, "Category")
    counts, probs, reliable = sequence.transition_matrix(events, "Category")
    print(f"\neligible customers (>=3 purchase events): {len(sequence.eligible_customers(events))}")
    print(f"self-transition rate: {sequence.self_transition_rate(counts):.1%}")

    df.to_pickle(outdir / "clean.pkl")
    events.to_pickle(outdir / "events.pkl")
    counts.to_csv(outdir / "transition_counts.csv")
    probs.to_csv(outdir / "transition_probs.csv")
    print(f"\nwrote outputs to {outdir}")


if __name__ == "__main__":
    main()
