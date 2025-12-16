from python.imports import *
from python.config import *

# -------------
# Dominant source tag filter
# -------------

def select_dominant_source_tag_with_fallback(
    df: pd.DataFrame,
    ticker_col: str = "ticker",
    label_col: str = "label",
    source_tag_col: str = "source_tag",
    end_col: str = "end",
    min_gap: int = 2,
) -> pd.DataFrame:
    """
    Select the dominant source_tag per (ticker, label), but if the dominant
    tag is absent for several consecutive periods, substitute observations
    from the second-most dominant tag for those periods.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    min_gap : int
        Minimum number of consecutive periods (years) the dominant tag must
        be absent before fallback is used.
    """

    df = df.copy()
    df[end_col] = pd.to_datetime(df[end_col], errors="coerce")
    df["year"] = df[end_col].dt.year

    # ----------------------------
    # 1. Rank source tags by usage
    # ----------------------------
    tag_counts = (
        df
        .groupby([ticker_col, label_col, source_tag_col])
        .size()
        .reset_index(name="n")
        .sort_values(
            by=[ticker_col, label_col, "n", source_tag_col],
            ascending=[True, True, False, True]
        )
    )

    # Keep top 2 tags per (ticker, label)
    top2 = (
        tag_counts
        .groupby([ticker_col, label_col])
        .head(2)
        .assign(rank=lambda x: x.groupby([ticker_col, label_col]).cumcount())
    )

    dominant = top2[top2["rank"] == 0]
    fallback = top2[top2["rank"] == 1]

    # ----------------------------
    # 2. Build dominant-only panel
    # ----------------------------
    df_dom = df.merge(
        dominant[[ticker_col, label_col, source_tag_col]],
        on=[ticker_col, label_col, source_tag_col],
        how="inner"
    )

    # ----------------------------
    # 3. Identify gaps in dominance
    # ----------------------------
    all_years = (
        df
        .groupby([ticker_col, label_col])["year"]
        .apply(lambda x: pd.Series(range(x.min(), x.max() + 1)))
        .reset_index()
        .rename(columns={0: "year"})
    )

    dom_years = (
        df_dom
        .groupby([ticker_col, label_col, "year"])
        .size()
        .reset_index(name="n")
    )

    year_grid = all_years.merge(
        dom_years,
        on=[ticker_col, label_col, "year"],
        how="left"
    ).assign(has_dom=lambda x: x["n"].notna())

    # Count consecutive gaps
    year_grid["gap_run"] = (
        year_grid
        .groupby([ticker_col, label_col])["has_dom"]
        .apply(lambda s: (~s).astype(int).groupby(s.cumsum()).cumsum())
        .reset_index(level=[0,1], drop=True)
    )

    gap_years = year_grid[
        (~year_grid["has_dom"]) & (year_grid["gap_run"] >= min_gap)
    ][[ticker_col, label_col, "year"]]

    # ----------------------------
    # 4. Pull fallback observations
    # ----------------------------
    if not fallback.empty:
        df_fb = df.merge(
            fallback[[ticker_col, label_col, source_tag_col]],
            on=[ticker_col, label_col, source_tag_col],
            how="inner"
        )
        df_fb = df_fb.merge(
            gap_years,
            on=[ticker_col, label_col, "year"],
            how="inner"
        )
    else:
        df_fb = df.iloc[0:0]

    # ----------------------------
    # 5. Combine dominant + fallback
    # ----------------------------
    out = (
        pd.concat([df_dom, df_fb], ignore_index=True)
        .sort_values([ticker_col, label_col, end_col])
    )

    return out


# -------------
# Quarterly filter
# -------------

def filter_quarterly_intervals(
    df: pd.DataFrame,
    start_col: str = "start",
    end_col: str = "end",
) -> pd.DataFrame:
    """
    Replicates the R pipeline:
      - converts start/end to dates
      - computes interval_days = end - start
      - keeps observations with 80 < interval_days < 120
    """

    df = df.copy()

    # Convert to datetime
    df[start_col] = pd.to_datetime(df[start_col], errors="coerce")
    df[end_col]   = pd.to_datetime(df[end_col], errors="coerce")

    # Compute interval length in days
    df["interval_days"] = (df[end_col] - df[start_col]).dt.days

    # Filter quarterly-length intervals
    df = df[
        (df["interval_days"] > 80) &
        (df["interval_days"] < 120)
    ]

    return df

# -------------
# Deduplication by latest filing
# -------------

def deduplicate_by_latest_filing(
    df: pd.DataFrame,
    group_cols=None,
    filed_col: str = "filed"
) -> pd.DataFrame:
    """
    Deduplicate SEC financial data by keeping, for each economic observation,
    the row associated with the most recently filed accession.

    Economic observation is defined by:
      (ticker, label, source_tag, start, end)

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    group_cols : list[str], optional
        Columns defining an economic observation.
        Defaults to ['ticker', 'label', 'source_tag', 'start', 'end'].
    filed_col : str
        Column containing filing date.

    Returns
    -------
    pd.DataFrame
        Deduplicated dataframe with exactly one row per economic observation.
    """

    if group_cols is None:
        group_cols = ["ticker", "label", "source_tag", "start", "end"]

    df = df.copy()

    # Ensure filed is datetime
    df[filed_col] = pd.to_datetime(df[filed_col], errors="coerce")

    # Sort so that most recent filing comes first
    df = df.sort_values(by=filed_col, ascending=False)

    # Drop duplicates, keeping the most recently filed row
    df = df.drop_duplicates(subset=group_cols, keep="first")

    return df


# -------------
# Collapse duplicates ignoring frame
# -------------

def collapse_duplicates_ignoring_frame(
    df: pd.DataFrame,
    identity_cols=None,
) -> pd.DataFrame:
    """
    Collapse rows that differ only by `frame` into a single row.

    Keeps one deterministic representative per economic observation.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    identity_cols : list[str], optional
        Columns defining economic identity.
        Defaults to ['ticker', 'label', 'source_tag', 'start', 'end'].

    Returns
    -------
    pd.DataFrame
        DataFrame with duplicates (by frame) collapsed.
    """

    if identity_cols is None:
        identity_cols = ["ticker", "label", "source_tag", "start", "end"]

    df = df.copy()

    # Deterministic ordering so result is reproducible
    if "frame" in df.columns:
        df = df.sort_values(by="frame")

    # Drop duplicates ignoring frame
    df = df.drop_duplicates(subset=identity_cols, keep="first")

    return df

# -------------
# Keep max interval observation
# -------------

def keep_max_interval_observation(
    df: pd.DataFrame,
    identity_cols=None,
    interval_col: str = "interval_days"
) -> pd.DataFrame:
    """
    For rows that are identical except for interval length,
    keep the observation with the largest interval_days.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    identity_cols : list[str], optional
        Columns defining economic identity EXCLUDING interval_days.
        Defaults to ['ticker', 'label', 'source_tag', 'end'].
    interval_col : str
        Column containing interval length in days.

    Returns
    -------
    pd.DataFrame
        DataFrame with conflicts resolved by keeping max interval.
    """

    if identity_cols is None:
        identity_cols = ["ticker", "label", "source_tag", "end"]

    df = df.copy()

    # Ensure interval_days is numeric
    df[interval_col] = pd.to_numeric(df[interval_col], errors="coerce")

    # Sort so largest interval comes first
    df = df.sort_values(by=interval_col, ascending=False)

    # Drop duplicates keeping the largest-interval row
    df = df.drop_duplicates(subset=identity_cols, keep="first")

    return df

# -------------
# Define boycotted indicator
# -------------

def define_boycotted(
    df: pd.DataFrame,
    boycotted_firm: str,
    boycott_start: str | pd.Timestamp = "2023-06-01",
    ticker_col: str = "ticker",
    end_col: str = "end",
) -> pd.DataFrame:
    """
    Add a binary 'boycotted' indicator:
      = 1 if firm is the boycotted firm and end >= boycott_start
      = 0 otherwise
    """

    df = df.copy()

    # Ensure end is datetime
    df[end_col] = pd.to_datetime(df[end_col], errors="coerce")

    boycott_start = pd.to_datetime(boycott_start)

    df["boycotted"] = (
        (df[ticker_col] == boycotted_firm) &
        (df[end_col] >= boycott_start)
    ).astype(int)

    return df

# -------------
# Add quarterly SCM-compatible time index
# -------------

def add_quarterly_time_index(
    df: pd.DataFrame,
    end_col: str = "end",
    time_col: str = "time"
) -> pd.DataFrame:
    """
    Add a quarterly SCM-compatible numeric time index:
      time = year(end) * 4 + quarter(end)

    Also adds helper columns: 'year' and 'quarter'.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    end_col : str
        Column containing period end date.
    time_col : str
        Name of the SCM time index column.

    Returns
    -------
    pd.DataFrame
        DataFrame with year, quarter, and time columns added.
    """

    df = df.copy()

    # Ensure end is datetime
    df[end_col] = pd.to_datetime(df[end_col], errors="coerce")

    # Extract year and quarter
    df["year"] = df[end_col].dt.year
    df["quarter"] = df[end_col].dt.quarter

    # SCM-compatible numeric time index
    df[time_col] = df["year"] * 4 + df["quarter"]

    return df

# -------------
# Resolve collisions preferring 10-K then latest end date
# -------------

def resolve_collisions_prefer_10k_then_latest_end(
    df: pd.DataFrame,
    identity_cols=None,
    form_col: str = "form",
    end_col: str = "end"
) -> pd.DataFrame:
    """
    Resolve collisions by:
      1) preferring rows whose form contains 'K' (10-K, 10-K/A)
      2) if still tied, preferring the row with the latest end date

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe (may contain collisions).
    identity_cols : list[str], optional
        Columns defining SCM identity.
        Defaults to ['ticker', 'label', 'time'].
    form_col : str
        Column containing SEC form (e.g. 10-K, 10-Q).
    end_col : str
        Column containing period end date.

    Returns
    -------
    pd.DataFrame
        DataFrame with collisions resolved.
    """

    if identity_cols is None:
        identity_cols = ["ticker", "label", "time"]

    df = df.copy()

    # Ensure correct types
    df[end_col] = pd.to_datetime(df[end_col], errors="coerce")

    # Indicator: prefer forms containing "K"
    df["_is_10k"] = df[form_col].astype(str).str.contains("K", case=False, na=False)

    # Sort by:
    # 1) is 10-K (True first)
    # 2) latest end date
    df = df.sort_values(
        by=identity_cols + ["_is_10k", end_col],
        ascending=[True] * len(identity_cols) + [False, False]
    )

    # Drop duplicates, keeping the preferred row
    df = df.drop_duplicates(subset=identity_cols, keep="first")

    # Cleanup
    df = df.drop(columns="_is_10k")

    return df






