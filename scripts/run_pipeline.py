"""Full pipeline: raw data -> clean -> category -> purchase events -> transition matrix.

Usage:
    python scripts/run_pipeline.py [--input path/to/online_retail_II.xlsx] [--outdir outputs]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import clean, pipeline, sequence  # noqa: E402
from src.category import category_quality  # noqa: E402


def main():
    args = pipeline.parse_args(__doc__)
    xlsx = pipeline.find_raw_xlsx(args.input)

    df, audit, n_raw = pipeline.load_clean_cached(xlsx, args.outdir)
    clean.print_audit(n_raw, audit, len(df))

    df, _, _ = pipeline.add_categories(df)
    quality = category_quality(df, "Category")
    print(f"\ncoverage: {quality['coverage']:.1%}")
    print(f"median dominant-category share: {quality['median_share']:.3f}")
    print(f"mixed-basket rate: {quality['mixed_basket_rate']:.1%}")

    events = sequence.build_purchase_events(df, "Category")
    counts, probs, _ = sequence.transition_matrix(events, "Category")
    print(f"\neligible customers (>=3 purchase events): {len(sequence.eligible_customers(events))}")
    print(f"self-transition rate: {sequence.self_transition_rate(counts):.1%}")

    df.to_pickle(args.outdir / "clean.pkl")
    events.to_pickle(args.outdir / "events.pkl")
    counts.to_csv(args.outdir / "transition_counts.csv")
    probs.to_csv(args.outdir / "transition_probs.csv")
    print(f"\nwrote outputs to {args.outdir}")


if __name__ == "__main__":
    main()
