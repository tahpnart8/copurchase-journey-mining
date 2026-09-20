# Customer Purchase Journeys from Transaction Sequences

Research code for a study on customer purchase journeys derived from
retail transaction sequences, using the Online Retail II dataset.

The central methodological question: retail transaction data rarely
ships with a product category taxonomy. This project generates one
from co-purchase behavior (community detection on a product network)
instead of assuming a taxonomy exists, then measures whether that
choice matters for downstream sequence analysis.

## Status

Data cleaning and category generation are implemented and validated.
Sequence construction, pattern mining, and journey clustering are in
progress; see Roadmap below.

## Repository structure

```
.
├── data/                  raw data goes here (not tracked, see data/README.md)
├── src/
│   ├── config.py          thresholds and paths, edit here rather than inline
│   ├── clean.py            five-step cleaning pipeline
│   ├── category.py         co-purchase graph, community detection, category assignment
│   ├── sequence.py         purchase-event construction, transition matrix
│   └── report_stats.py     descriptive statistics
├── scripts/
│   └── run_pipeline.py     end-to-end CLI entry point
├── outputs/                 generated artifacts (not tracked)
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download the dataset per `data/README.md`, then:

```bash
python scripts/run_pipeline.py --input data/online_retail_II.xlsx --outdir outputs
```

## Method summary

**Cleaning.** Five steps applied in order: drop cancelled invoices
(Invoice prefix `C`), drop rows with no Customer ID, drop non-positive
Quantity or Price, drop service/fee codes (postage, bank charges, and
similar non-product lines), drop exact duplicate rows. Order matters:
changing it changes how many rows each step removes, though not the
final result. See `src/clean.py`.

**Category generation.** A co-purchase graph is built over all SKUs:
two products are connected if they co-occur in at least
`MIN_CO_OCCURRENCE` invoices with lift at least `MIN_LIFT`. Communities
are detected with Louvain (`src/category.py`); the ten largest become
the official product categories, the remainder is labelled `OTHER`.
This is compared against a keyword-rule baseline on three metrics:
category coverage, median revenue share of the dominant category per
purchase event, and the rate of mixed-category purchase events.

**Sequences.** Same-day invoices for a customer are merged into a
single purchase event, since a meaningful share of same-day invoice
pairs reflects operational order-splitting rather than two separate
purchase decisions. Each event is labelled by its revenue-dominant
category. Customers with at least `MIN_SEQUENCE_LENGTH` events are
eligible for sequence analysis (`src/sequence.py`).

## Roadmap

1. Sequential pattern mining and association rules on constructed sequences
2. First-order Markov transition matrix with reliability flags per cell
3. Journey-type clustering on sequence-derived features
4. Baseline comparison against RFM clustering on the same customers
5. Stability check across a time-based train/test split

## Data

Chen, D., Sain, S. L., & Guo, K. (2012). Data mining for the online
retail industry: A case study of RFM model-based customer segmentation
using data mining. *Journal of Database Marketing & Customer Strategy
Management, 19*(3), 197-208. https://doi.org/10.1057/dbm.2012.17

## License

MIT (see LICENSE).
