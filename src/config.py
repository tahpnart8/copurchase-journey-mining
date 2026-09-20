"""Shared constants and thresholds. Change parameters here, not inline elsewhere."""

from pathlib import Path

# paths
DATA_DIR = Path("data")
RAW_XLSX = DATA_DIR / "online_retail_II.xlsx"
OUTPUT_DIR = Path("outputs")

# cleaning
SERVICE_CODES = {
    "POST", "DOT", "M", "m", "C2", "D", "S", "B", "BANK CHARGES", "ADJUST",
    "AMAZONFEE", "PADS", "CRUK", "TEST001", "TEST002",
    "gift_0001_10", "gift_0001_20", "gift_0001_30", "gift_0001_40",
    "gift_0001_50", "gift_0001_60", "gift_0001_70", "gift_0001_80",
    "gift_0001_90",
}

# co-purchase network
MIN_CO_OCCURRENCE = 10      # minimum invoices two products must share an edge
MIN_LIFT = 3                 # minimum lift to keep an edge
MAX_BASKET_SIZE = 60          # baskets larger than this are skipped when counting pairs
LOUVAIN_RESOLUTION = 0.5
LOUVAIN_SEED = 42
N_CATEGORIES = 10             # top communities kept as official categories, rest -> OTHER

# sequences
MIN_SEQUENCE_LENGTH = 3       # minimum purchase events for a customer to be eligible
MIN_CELL_OBSERVATIONS = 30    # transition matrix cells below this are unreliable

RANDOM_STATE = 42
