from python.imports import *
from python.config import *

# ---------- UTIL / FETCH ----------
# Load SEC ticker to CIK mapping
def load_ticker_map() -> Dict[str, str]:
    url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    j = r.json()
    return {v["ticker"].upper(): f'{int(v["cik_str"]):010d}' for v in j.values()}

# ---------- FETCHING / PARSING ----------
def _get_json(url: str, timeout=30, max_retries=5):
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()

        except requests.exceptions.ReadTimeout:
            time.sleep(2 ** attempt)

    return None

# Returns all reported values for a single XBRL tag
def company_concept(cik10: str, taxonomy: str, tag: str):
    url = f"{BASE}/xbrl/companyconcept/CIK{cik10}/{taxonomy}/{tag}.json"
    return _get_json(url)

# Converts SEC concept JSON to DataFrame
def concept_to_df(j: dict) -> pd.DataFrame:
    if j is None:
        return pd.DataFrame(columns=["start", "end", "val", "accn", "fy", "fp", "form", "filed"])
    
    units = j.get("units", {})

    unit_key = None
    if unit_key is None and units:
        unit_key = next(iter(units))

    rows = units.get(unit_key, [])
    if not rows:
        return pd.DataFrame(columns=["start", "end", "val", "accn", "fy", "fp", "form", "filed"])
    
    # Build DataFrame
    df = pd.DataFrame(rows)

    for c in ("start", "end", "val", "accn", "fy", "fp", "form", "filed"):
        if c not in df.columns: df[c] = pd.NA
        
    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["end"] = pd.to_datetime(df["end"], errors="coerce")
    df["val"] = pd.to_numeric(df["val"], errors="coerce")
    df["fy"] = pd.to_numeric(df["fy"], errors="coerce").astype("Int64")

    return df.sort_values(["end", "fy"], na_position="last")


# Fetch all tags in a tag group with provenance
def fetch_all_tags(
    cik10: str,
    tags: list[str],
) -> pd.DataFrame:
    """
    Fetch all tags in a tag group and retain provenance.
    One row per (time × tag).
    """

    dfs = []

    for tag in tags:
        j = company_concept(cik10, "us-gaap", tag)

        if j is None:
            # Explicitly record missing tags (optional but useful)
            print(f"[{tag}] Tag not found: {tag}")
            continue

        time.sleep(0.3)  # Be polite to SEC servers

        df = concept_to_df(j)
        if df.empty:
            print(f"[{tag}] Tag empty: {tag}")
            continue

        # Add provenance columns
        df["source_tag"] = tag

        dfs.append(df)

        print(f"[{tag}] Collected tag: {tag} ({len(df)} rows)")

    if not dfs:
        return pd.DataFrame(
            columns=[
                "start", "end", "val", "accn", "fy", "fp", "form", "filed", "source_tag"
            ]
        )

    return pd.concat(dfs, ignore_index=True)


def collect_concepts_long(
    tickers: list[str],
    tags: list[str],
    taxonomy: str = "us-gaap"
) -> pd.DataFrame:
    """
    Apply concept_to_df to every (ticker × tag) pair
    and return one long DataFrame with provenance.
    """

    ticker_map = load_ticker_map()
    dfs = []

    for ticker in tickers:
        ticker = ticker.upper()

        if ticker not in ticker_map:
            print(f"Ticker not found: {ticker}")
            continue

        cik10 = ticker_map[ticker]

        for tag in tags:
            j = company_concept(cik10, taxonomy, tag)
            
            time.sleep(0.3)
            
            if j is None:
                continue

            df = concept_to_df(j)

            if df.empty:
                continue

            df["ticker"] = ticker
            df["source_tag"] = tag

            dfs.append(df)

    if not dfs:
        return pd.DataFrame(
            columns=[
                "ticker",
                "start", "end", "val",
                "accn", "fy", "fp",
                "form", "filed",
                "source_tag",
            ]
        )

    return pd.concat(dfs, ignore_index=True)

