from imports import *
from config import *
from scraping import *
from tagging import *
from preprocessing import *

# this module provides diagnostics functions for financial data

# the next diagnostic checks the overlap of reporting periods across different firms for each calendar quarter
# %%

input_path = "../data/raw/financials_batch_3.csv"

df = pd.read_csv(input_path)

     # -----------------
    # Add year and quarter
    # -----------------
df = add_year_quarter(df)
    # -----------------
    # Quarterly filter + interval_days
    # -----------------
df = filter_quarterly_intervals(df)
cols = ["ticker", "start", "end"]
df = df[cols + [c for c in df.columns if c not in cols]]

df["start"] = pd.to_datetime(df["start"])
df["end"]   = pd.to_datetime(df["end"])


df["cal_period"] = (
        df["year"].astype(str) + "Q" + df["quarter"].astype(str)
)

df_rev = df[df["label"] == "revenue"].copy()
df_rev_2025Q1 = df_rev[df_rev["cal_period"] == "2025Q1"].copy()


def overlap_days(a_start, a_end, b_start, b_end):
        latest_start = max(a_start, b_start)
        earliest_end = min(a_end, b_end)

        return max((earliest_end - latest_start).days + 1, 0)

records = []

for period, g in df_rev_2025Q1.groupby("cal_period"):

        # Common overlap window across all units in this period
        common_start = g["start"].max()
        common_end   = g["end"].min()

        if common_start > common_end:
            # No common overlap at all
            for _, row in g.iterrows():
                records.append({
                    "ticker": row["ticker"],
                   
                    "overlap_ratio": 0.0,
                    "has_common_overlap": False
                })
            continue

        common_length = (common_end - common_start).days + 1

        for _, row in g.iterrows():
            unit_length = (row["end"] - row["start"]).days + 1
            odays = overlap_days(
                row["start"], row["end"],
                common_start, common_end
            )

            records.append({
                    "ticker": row["ticker"],
               
                    "unit_length_days": unit_length,
                    "common_length_days": common_length,
                    "overlap_days": odays,
                    "overlap_ratio": odays / unit_length if unit_length > 0 else np.nan,
                    "has_common_overlap": odays > 0
            })

        overlap_df = pd.DataFrame(records)
        overlap_df["overlap_ratio"].describe()

        (overlap_df
            .groupby("ticker")["overlap_ratio"]
            .mean()
            .sort_values())
        
        
        problematic = overlap_df[overlap_df["overlap_ratio"] < 0.3]

def overlapping_dates(start_dates, end_dates):
    common_start = start_dates.max()
    common_end   = end_dates.min()

    if common_start > common_end:
        return []

    return pd.date_range(common_start, common_end, freq="D")

for period, g in df.groupby("cal_period"):

    overlap_days = overlapping_dates(g["start"], g["end"])

    print(f"\n📅 Calendar period: {period}")

    if len(overlap_days) == 0:
        print("  ❌ No overlapping days across units")
    else:
        print(f"  ✅ Overlapping window: {overlap_days[0].date()} → {overlap_days[-1].date()}")
        print(f"  📊 Number of overlapping days: {len(overlap_days)}")
     



TREATED_TICKER = "MCD"   # change if needed
MIN_OVERLAP_DAYS = 10
POST_START = "2023Q4"



def overlap_days(a_start, a_end, b_start, b_end):
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    return max((earliest_end - latest_start).days + 1, 0)



post_periods = (
    df.loc[df["cal_period"] >= POST_START, "cal_period"]
      .unique()
)


treated_df = df[df["ticker"] == TREATED_TICKER].copy()
donor_df   = df[df["ticker"] != TREATED_TICKER].copy()

valid_donors = []

for donor in donor_df["ticker"].unique():

    donor_ok = True
    donor_rows = donor_df[donor_df["ticker"] == donor]

    for period in post_periods:

        d_p = donor_rows[donor_rows["cal_period"] == period]
        t_p = treated_df[treated_df["cal_period"] == period]

        # donor or treated unit missing in this period → invalid
        if d_p.empty or t_p.empty:
            donor_ok = False
            break

        odays = overlap_days(
            d_p.iloc[0]["start"], d_p.iloc[0]["end"],
            t_p.iloc[0]["start"], t_p.iloc[0]["end"]
        )

        if odays < MIN_OVERLAP_DAYS:
            donor_ok = False
            break

    if donor_ok:
        valid_donors.append(donor)

    df_restricted = df[
        (df["ticker"] == TREATED_TICKER) |
        (df["ticker"].isin(valid_donors))
    ].copy()

    print("Number of valid donors:", len(valid_donors))
    print("Valid donors:", valid_donors)


df_rev = df[df["label"] == "revenue"].copy()
WINDOW_DAYS = 45

groups = []

for start_date, g in df_rev.groupby("start"):

    if len(g) < 2:
        continue  # nothing to compare

    g = g.sort_values("end")

    for i, row in g.iterrows():

        close = g[
            (g["end"] >= row["end"] - pd.Timedelta(days=WINDOW_DAYS)) &
            (g["end"] <= row["end"] + pd.Timedelta(days=WINDOW_DAYS))
        ]

        if len(close) > 1:
            groups.append(close)

seen = set()

for g in groups:
    key = tuple(sorted(g["ticker"].tolist()))
    if key in seen:
        continue
    seen.add(key)

    print("\n📌 Same start date:", g["start"].iloc[0].date())
    print("End date range:",
          g["end"].min().date(), "→", g["end"].max().date())
    print(g[["ticker", "start", "end", "label"]])


WINDOW_DAYS = 30
clusters = []

used_idx = set()

for i, row in df_rev.iterrows():

    if i in used_idx:
        continue

    close = df_rev[
        (df_rev["start"] >= row["start"] - pd.Timedelta(days=WINDOW_DAYS)) &
        (df_rev["start"] <= row["start"] + pd.Timedelta(days=WINDOW_DAYS)) &
        (df_rev["end"]   >= row["end"]   - pd.Timedelta(days=WINDOW_DAYS)) &
        (df_rev["end"]   <= row["end"]   + pd.Timedelta(days=WINDOW_DAYS))
    ]

    if len(close) > 1:
        clusters.append(close)
        used_idx.update(close.index)



for g in clusters:
    print("\n📌 Similar reporting window cluster")
    print("Start range:",
          g["start"].min().date(), "→", g["start"].max().date())
    print("End range:",
          g["end"].min().date(), "→", g["end"].max().date())
    print(g[["ticker", "start", "end"]])



TREATED_TICKER = "MCD"
WINDOW_DAYS = 45

mcd = df_rev[df_rev["ticker"] == TREATED_TICKER]
donors = df_rev[df_rev["ticker"] != TREATED_TICKER]

matches = []

for _, mcd_row in mcd.iterrows():

    mcd_start = mcd_row["start"]
    mcd_end   = mcd_row["end"]

    close_donors = donors[
        (donors["start"] >= mcd_start - pd.Timedelta(days=WINDOW_DAYS)) &
        (donors["start"] <= mcd_start + pd.Timedelta(days=WINDOW_DAYS)) &
        (donors["end"]   >= mcd_end   - pd.Timedelta(days=WINDOW_DAYS)) &
        (donors["end"]   <= mcd_end   + pd.Timedelta(days=WINDOW_DAYS))
    ].copy()

    if not close_donors.empty:
        close_donors["mcd_start"] = mcd_start
        close_donors["mcd_end"]   = mcd_end
        matches.append(close_donors)


if matches:
    result = pd.concat(matches).drop_duplicates()
    print(result[[
        "ticker",
        "start",
        "end",
        "mcd_start",
        "mcd_end"
    ]].sort_values(["mcd_end", "ticker"]))
else:
    print("No donors found within ±45 days of MCD reporting windows.")


valid_donor_rows = []

for _, mcd_row in mcd.iterrows():

    mcd_start = mcd_row["start"]
    mcd_end   = mcd_row["end"]

    close = donors[
        (donors["start"] >= mcd_start - pd.Timedelta(days=WINDOW_DAYS)) &
        (donors["start"] <= mcd_start + pd.Timedelta(days=WINDOW_DAYS)) &
        (donors["end"]   >= mcd_end   - pd.Timedelta(days=WINDOW_DAYS)) &
        (donors["end"]   <= mcd_end   + pd.Timedelta(days=WINDOW_DAYS))
    ]

    valid_donor_rows.append(close)

donor_df = pd.concat(valid_donor_rows).drop_duplicates()


donor_list = sorted(donor_df["ticker"].unique())

print("Number of valid donors:", len(donor_list))
print("Donor tickers:", donor_list)

import pandas as pd

TREATED_TICKER = "MCD"

df["start"] = pd.to_datetime(df["start"])
df["end"]   = pd.to_datetime(df["end"])

# focus on revenue only
df_rev = df[df["label"] == "revenue"].copy()

# split treated and donors
mcd = df_rev[df_rev["ticker"] == TREATED_TICKER]
donors = df_rev[df_rev["ticker"] != TREATED_TICKER]

def overlap_days(a_start, a_end, b_start, b_end):
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    return max((earliest_end - latest_start).days + 1, 0)

records = []

for _, mcd_row in mcd.iterrows():

    for _, donor_row in donors.iterrows():

        odays = overlap_days(
            mcd_row["start"], mcd_row["end"],
            donor_row["start"], donor_row["end"]
        )

        records.append({
            "donor": donor_row["ticker"],
            "mcd_start": mcd_row["start"],
            "mcd_end": mcd_row["end"],
            "donor_start": donor_row["start"],
            "donor_end": donor_row["end"],
            "overlap_days": odays
        })

overlap_df = pd.DataFrame(records)

# summary by donor
(overlap_df
 .groupby("donor")["overlap_days"]
 .describe()
 .sort_values("mean"))

# check minimum overlap (important)
(overlap_df
 .groupby("donor")["overlap_days"]
 .max()
 .sort_values())


df["cal_year"] = df["end"].dt.year
df["cal_quarter"] = df["end"].dt.quarter
df["cal_period"] = (
    df["cal_year"].astype(str) + "Q" + df["cal_quarter"].astype(str)
)


records = []

for period, g in df_rev.groupby("cal_period"):

    common_start = g["start"].max()
    common_end   = g["end"].min()

    if common_start > common_end:
        overlap = 0
    else:
        overlap = (common_end - common_start).days + 1

    records.append({
        "cal_period": period,
        "common_overlap_days": overlap,
        "n_units": len(g)
    })

period_overlap_df = pd.DataFrame(records)

# make sure dates are datetime
df["start"] = pd.to_datetime(df["start"])
df["end"]   = pd.to_datetime(df["end"])

# create calendar period from END date (correct choice)
df["cal_year"] = df["end"].dt.year
df["cal_quarter"] = df["end"].dt.quarter

df["cal_period"] = (
    df["cal_year"].astype(str)
    + "Q"
    + df["cal_quarter"].astype(str)
)

df_rev = df[df["label"] == "revenue"].copy()

records = []

for period, g in df_rev.groupby("cal_period"):

    common_start = g["start"].max()
    common_end   = g["end"].min()

    if common_start > common_end:
        overlap = 0
    else:
        overlap = (common_end - common_start).days + 1

    records.append({
        "cal_period": period,
        "common_overlap_days": overlap,
        "n_units": len(g)
    })

period_overlap_df = pd.DataFrame(records)


# %%
