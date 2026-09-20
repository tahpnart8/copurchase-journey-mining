# Data

This directory is intentionally empty in version control. The raw file is
not redistributed here; download it directly from the source.

## Source

Online Retail II, UCI Machine Learning Repository
https://archive.ics.uci.edu/dataset/502/online+retail+ii

Chen, D., Sain, S. L., & Guo, K. (2012). Data mining for the online retail
industry: A case study of RFM model-based customer segmentation using data
mining. *Journal of Database Marketing & Customer Strategy Management,
19*(3), 197-208. https://doi.org/10.1057/dbm.2012.17

## Setup

Download `online_retail_II.xlsx` and place it in this directory:

```
data/online_retail_II.xlsx
```

## Note on the two sheets

The file ships as two sheets, `Year 2009-2010` and `Year 2010-2011`. They
overlap by about nine days at the end of 2010 (identical rows appear in
both sheets for that window). `src/clean.py` concatenates both sheets
without tagging rows by sheet of origin, so `drop_duplicates()` correctly
removes this overlap. Tagging rows by source sheet before deduplication
undercounts duplicates by roughly 14,000 rows.
