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
      - keeps observations with 60 < interval_days < 122
    """

    df = df.copy()

    # Convert to datetime
    df[start_col] = pd.to_datetime(df[start_col], errors="coerce")
    df[end_col]   = pd.to_datetime(df[end_col], errors="coerce")

    # Compute interval length in days
    df["interval_days"] = (df[end_col] - df[start_col]).dt.days

    # Filter quarterly-length intervals
    df = df[
        (df["interval_days"] > 60) &
        (df["interval_days"] < 122)
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

def add_year_quarter(
    df: pd.DataFrame,
    end_col: str = "end",
    time_col: str = "time"
) -> pd.DataFrame:
    """
    Adds helper columns: 'year' and 'quarter'.

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
        DataFrame with year, quarter columns added
    """

    df = df.copy()

    # Ensure end is datetime
    df[end_col] = pd.to_datetime(df[end_col], errors="coerce")

    # Extract year and quarter
    df["year"] = df[end_col].dt.year
    df["quarter"] = df[end_col].dt.quarter

    return df

def add_scm_time_index(
    df: pd.DataFrame,
    time_col: str = "time"
) -> pd.DataFrame:
    """
    Adds a SCM-compatible numeric time index.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    time_col : str
        Name of the SCM time index column.

    Returns
    -------
    pd.DataFrame
        DataFrame with SCM time index added.
    """

    df = df.copy()

    # Ensure year and quarter are present
    if "year" not in df.columns or "quarter" not in df.columns:
        raise ValueError("DataFrame must contain 'year' and 'quarter' columns.")

    # SCM-compatible numeric time index
    df[time_col] = df["year"] * 4 + df["quarter"]

    return df


# -------------
# Resolve collisions preferring 10-K then latest end date
# -------------

def resolve_collisions_prefer_10q_then_latest_end(
    df: pd.DataFrame,
    identity_cols=None,
    form_col: str = "form",
    end_col: str = "end"
) -> pd.DataFrame:
    """
    Resolve collisions by:
      1) preferring rows whose form contains 'Q' (10-Q, 10-Q/A)
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
    df["_is_10q"] = df[form_col].astype(str).str.contains("Q", case=False, na=False)

    # Sort by:
    # 1) is 10-Q (True first)
    # 2) latest end date
    df = df.sort_values(
        by=identity_cols + ["_is_10q", end_col],
        ascending=[True] * len(identity_cols) + [False, False]
    )

    # Drop duplicates, keeping the preferred row
    df = df.drop_duplicates(subset=identity_cols, keep="first")

    # Cleanup
    df = df.drop(columns="_is_10q")

    return df


# -------------
# Refine estimation window
# -------------

def refine_estimation_window(
    df: pd.DataFrame,
    time_col: str = "time",
    start_time: int | None = None,
    end_time: int | None = None,
) -> pd.DataFrame:
    """
    Keep only rows within [start_time, end_time] on the SCM time index.
    If start_time or end_time is None, it is left unbounded on that side.
    """
    out = df.copy()

    if start_time is not None:
        out = out[out[time_col] >= start_time]
    if end_time is not None:
        out = out[out[time_col] <= end_time]

    return out

# -------------
# Drop chronically sparse donors
# -------------

def drop_chronically_sparse_donors(
    df: pd.DataFrame,
    unit_col: str = "ticker",
    time_col: str = "time",
    label_col: str = "label",
    outcome_label: str = "revenue",
    treat_col: str = "boycotted",
    min_pre_coverage: float = 0.7,
    pre_period_end: int | None = None,
) -> pd.DataFrame:
    """
    Drop donor units with low pre-treatment coverage for a specific outcome label.

    Coverage is measured as:
      (# observed pre-treatment time points for unit) / (# total pre-treatment time points in sample)

    Parameters
    ----------
    outcome_label : str
        Which label to use to assess coverage (typically the outcome you're estimating).
    min_pre_coverage : float
        Minimum required share of pre-treatment periods observed (0 to 1).
    pre_period_end : int | None
        If provided, defines pre-treatment as time <= pre_period_end.
        If None, pre-treatment is inferred as treat_col == 0 rows.

    Notes
    -----
    - The treated unit(s) are never dropped.
    - This function assumes one row per (unit, time, label) in the long data.
    """
    out = df.copy()

    # Identify treated units (never drop)
    treated_units = set(out.loc[out[treat_col] == 1, unit_col].unique())

    # Work on outcome label only to compute coverage
    sub = out[out[label_col] == outcome_label].copy()

    # Define pre-treatment mask
    if pre_period_end is not None:
        pre_mask = sub[time_col] <= pre_period_end
    else:
        pre_mask = sub[treat_col] == 0

    sub_pre = sub[pre_mask].copy()

    # Total pre-treatment time points available in the sample
    pre_times = sub_pre[time_col].dropna().unique()
    total_pre_T = len(pre_times)
    if total_pre_T == 0:
        # Nothing to evaluate; return unchanged
        return out

    # Observed pre-treatment time points per unit
    obs_pre = (
        sub_pre
        .dropna(subset=[time_col])
        .groupby(unit_col)[time_col]
        .nunique()
        .rename("observed_pre_T")
        .reset_index()
    )
    obs_pre["pre_coverage"] = obs_pre["observed_pre_T"] / total_pre_T

    # Units to keep: treated always, donors only if coverage >= threshold
    keep_units = set(
        obs_pre.loc[obs_pre["pre_coverage"] >= min_pre_coverage, unit_col].unique()
    ) | treated_units

    out = out[out[unit_col].isin(keep_units)].copy()
    return out

# -------------
# Pivot wide for gsynth
# -------------

def pivot_wide(
    df: pd.DataFrame,
    unit_col: str = "ticker",
    time_col: str = "time",
    label_col: str = "label",
    value_col: str = "val",
    keep_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Pivot long data (label/value) into a wide panel (one row per unit-time).
    Keeps specified non-label columns (e.g. boycotted) by taking the first value
    within each unit-time group.

    Parameters
    ----------
    keep_cols : list[str] | None
        Columns to keep as-is (not pivoted). Typical: ['boycotted'] (and maybe 'end').
    """
    if keep_cols is None:
        keep_cols = ["boycotted"]

    # Ensure uniqueness before pivot (otherwise pivot will error or aggregate unexpectedly)
    if df.duplicated(subset=[unit_col, time_col, label_col]).any():
        raise ValueError("Cannot pivot: duplicate (unit, time, label) rows exist.")

    # Non-pivot columns: collapse to one value per (unit, time)
    meta = (
        df[[unit_col, time_col] + [c for c in keep_cols if c in df.columns]]
        .drop_duplicates(subset=[unit_col, time_col])
    )

    wide = (
        df.pivot(index=[unit_col, time_col], columns=label_col, values=value_col)
          .reset_index()
    )

    out = wide.merge(meta, on=[unit_col, time_col], how="left")

    # Optional: flatten column names if label column becomes a MultiIndex (rare)
    out.columns = [str(c) for c in out.columns]

    return out


def complete_scm_time_grid(
    df: pd.DataFrame,
    unit_col: str,
    time_col: str,
) -> pd.DataFrame:
    """
    Complete SCM-style integer time grid within each unit.

    Example time_col: 8034, 8035, 8036, ...

    Creates missing (unit, time) rows between each unit's
    observed min and max time.
    """

    df = df.copy()

    # Enforce integer time index
    if not np.issubdtype(df[time_col].dtype, np.integer):
        raise TypeError(f"{time_col} must be integer for SCM-style time")

    df = df.sort_values([unit_col, time_col])

    completed = []

    for unit, g in df.groupby(unit_col):
        t_min = int(g[time_col].min())
        t_max = int(g[time_col].max())

        full_time = pd.DataFrame({
            unit_col: unit,
            time_col: np.arange(t_min, t_max + 1)
        })

        g_full = full_time.merge(
            g,
            on=[unit_col, time_col],
            how="left"
        )

        completed.append(g_full)

    return pd.concat(completed, ignore_index=True)

# -------------
# Impute all numeric columns within unit
# -------------

def impute_all_numeric_within_unit(
    df: pd.DataFrame,
    unit_col: str,
    time_col: str,
    exclude_cols: list = None,
    method: str = "both"
) -> pd.DataFrame:
    """
    Impute ALL numeric columns within each unit using forward/backward fill.

    Parameters
    ----------
    df : pd.DataFrame
        Panel dataframe.
    unit_col : str
        Unit identifier (e.g. 'ticker').
    time_col : str
        Time variable (sortable).
    exclude_cols : list, optional
        Columns to exclude from imputation (IDs, treatment, etc.).
    method : {'forward', 'backward', 'both'}
        Direction of imputation.

    Returns
    -------
    pd.DataFrame
        Imputed dataframe.
    """

    df = df.copy()
    exclude_cols = exclude_cols or []

    # Identify numeric columns only
    numeric_cols = (
        df.select_dtypes(include=[np.number])
          .columns
          .difference([unit_col, time_col] + exclude_cols)
          .tolist()
    )

    df = df.sort_values([unit_col, time_col])

    def _impute(group):
        if method in ("forward", "both"):
            group[numeric_cols] = group[numeric_cols].ffill()
        if method in ("backward", "both"):
            group[numeric_cols] = group[numeric_cols].bfill()
        return group

    return df.groupby(unit_col, group_keys=False).apply(_impute)


def standardize_by_period0(

    df: pd.DataFrame,
    unit_col: str,
    time_col: str,
    cols: list,
    method: str = "ratio",   # "ratio" or "diff"
    suffix: str = "_std"
) -> pd.DataFrame:
    """
    Standardize variables by unit-specific period 0.

    For each unit i:
        ratio: X_it / X_i0
        diff:  X_it - X_i0

    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    unit_col : str
        Unit identifier (e.g. 'ticker').
    time_col : str
        Time variable (sortable).
    cols : list
        Columns to standardize.
    method : {"ratio", "diff"}
        Standardization method.
    suffix : str
        Suffix for standardized variables.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized columns added.
    """

    df = df.copy()
    df = df.sort_values([unit_col, time_col])

    # Get period-0 values per unit
    baseline = (
        df.groupby(unit_col, as_index=False)
          .first()[[unit_col] + cols]
          .rename(columns={c: f"{c}_p0" for c in cols})
    )

    df = df.merge(baseline, on=unit_col, how="left")

    for c in cols:
        p0 = f"{c}_p0"
        out = f"{c}{suffix}"

        if method == "ratio":
            df[out] = np.where(
                df[p0].notna() & (df[p0] != 0),
                df[c] / df[p0],
                np.nan
            )
        elif method == "diff":
            df[out] = np.where(
                df[p0].notna(),
                df[c] - df[p0],
                np.nan
            )
        else:
            raise ValueError("method must be 'ratio' or 'diff'")

    # Optional: drop baseline helper columns
    df.drop(columns=[f"{c}_p0" for c in cols], inplace=True)

    return df

