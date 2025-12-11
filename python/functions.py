from imports import *
from config import *
from tag_groups import *

# ---------- UTIL / FETCH ----------
# Load SEC ticker to CIK mapping
def load_ticker_map() -> Dict[str, str]:
    url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    j = r.json()
    return {v["ticker"].upper(): f'{int(v["cik_str"]):010d}' for v in j.values()}

# ---------- FETCHING / PARSING ----------
def _get_json(url: str):
    r = requests.get(url, headers=UA, timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()

# Returns all reported values for a single XBRL tag
def company_concept(cik10: str, taxonomy: str, tag: str):
    url = f"{BASE}/xbrl/companyconcept/CIK{cik10}/{taxonomy}/{tag}.json"
    return _get_json(url)

# Converts SEC concept JSON to DataFrame
def concept_to_df(j: dict, prefer_units=("USD", "USD$", "USD (in millions)")) -> pd.DataFrame:
    if j is None:
        return pd.DataFrame(columns=["fy", "fp", "start", "end", "val"])
    units = j.get("units", {})
    unit_key = None
    for u in prefer_units:
        if u in units:
            unit_key = u
            break
    if unit_key is None and units:
        unit_key = next(iter(units))
    rows = units.get(unit_key, [])
    if not rows:
        return pd.DataFrame(columns=["fy", "fp", "start", "end", "val"])
    df = pd.DataFrame(rows)

    for c in ("fy", "fp", "start", "end", "val"):
        if c not in df.columns: df[c] = pd.NA
        
    df["fy"] = pd.to_numeric(df["fy"], errors="coerce").astype("Int64")
    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["end"] = pd.to_datetime(df["end"], errors="coerce")
    return df.sort_values(["end", "fy"], na_position="last")[["fy", "fp", "start", "end", "val"]]

# Try several possible tag names and return the first one that has real SEC data for this company.
def _fetch_first_available(cik10: str, tags: List[str], label: str = "") -> pd.DataFrame:
    for tag in tags:
        j = company_concept(cik10, "us-gaap", tag)
        if j is None:
            continue
        df = concept_to_df(j)
        if not df.empty:
            print(f"[{label}] Using tag: {tag}")
            return df
        time.sleep(0.2)
    print(f"[{label}] No data for tags: {tags}")
    return pd.DataFrame(columns=["fy", "fp", "start", "end", "val"])

# ---------- MAIN FUNCTIONS ----------

# Extract quarterly datapoints from SEC fact dataframe.
def quarterly_series(df: pd.DataFrame) -> pd.DataFrame:

    q = df[df["fp"].str.upper().str.startswith("Q")].copy()

    if q.empty:
        return pd.DataFrame(columns=["fy", "fp", "start", "end", "val"])
    q["qnum"] = q["fp"].str.upper().str.extract(r"Q(\d)").astype("Int64")

    # keep one row per fiscal year + quarter
    q = (
        q.sort_values("end")
          .groupby(["fy","qnum"], dropna=True)
          .agg(val=("val","last"),
               end=("end","last"),
               start=("start","last"))
          .reset_index()
    )
    
    q["fp"] = "Q" + q["qnum"].astype("Int64").astype(str)
    return q[["fy", "fp", "start", "end", "val"]].sort_values(["fy","fp"])

# Extract annual datapoints from SEC fact dataframe.
def annual_series(df: pd.DataFrame) -> pd.DataFrame:
    """Extract annual datapoints from SEC fact dataframe."""
    if df.empty:
        return pd.DataFrame(columns=["fy", "fp", "start", "end", "val"])

    annual_flags = ["FY", "Y", "CY", "ANN", "ANNUAL"]

    a = df[df["fp"].str.upper().isin(annual_flags)].copy()
    if a.empty:
        return pd.DataFrame(columns=["fy", "fp", "start", "end", "val"])

    a = (
        a.sort_values("end")
         .groupby("fy", dropna=True)
         .agg(val=("val", "last"), end=("end", "last"), start=("start", "last"))
         .reset_index()
    )
    a["fp"] = "FY"

    return a[["fy", "fp", "end", "start", "val"]].sort_values("fy")

# Helper to add both quarterly and annual series for a given set of tags
def _add_column_both(cik10, tags, colname, label=""):
    raw = _fetch_first_available(cik10, tags, label=label)
    q = quarterly_series(raw).rename(columns={"val": colname})
    a = annual_series(raw).rename(columns={"val": colname})
    q["frequency"] = "Q"
    a["frequency"] = "A"
    return q, a

# Main function to get financials for a given ticker
def get_financials(ticker: str, last_n_quarters: int = 16) -> pd.DataFrame:
    tmap = load_ticker_map()
    cik10 = tmap[ticker.upper()]

    quarts = []
    annuals = []

    def add(tags, col, label):
        q, a = _add_column_both(cik10, tags, col, label)
        quarts.append(q)
        annuals.append(a)

    # ---- Core metrics ----
    add(REVENUE_TAGS, "revenue", "Revenue")
    add(GROSS_PROFIT_TAGS, "gross_profit", "Gross Profit")
    add(NET_INCOME_TAGS, "net_income", "Net Income")
    add(OPERATING_EXP_TAGS, "operating_expenses", "Operating Exp")
    add(R_AND_D_TAGS, "r_and_d", "R&D")
    add(DEPR_AMORT_TAGS, "depr_amort", "D&A")
    add(INTEREST_EXP_TAGS, "interest_expense", "Interest Exp")
    add(INTEREST_INC_TAGS, "interest_income", "Interest Inc")
    add(INCOMEBEFORETAX_TAGS, "income_before_tax", "Income Before Tax")
    add(TAX_TAGS, "tax_expense", "Tax Expense")
    add(EPS_BASIC_TAGS, "eps_basic", "EPS Basic")
    add(EPS_DILUTED_TAGS, "eps_diluted", "EPS Diluted")
    add(SHARES_BASIC_TAGS, "shares_basic", "Shares Basic")
    add(SHARES_DILUTED_TAGS, "shares_diluted", "Shares Diluted")
    add(ASSETS_TAGS, "assets", "Assets")
    add(ASSETS_CURR_TAGS, "assets_current", "Assets Current")
    add(LIAB_TAGS, "liabilities", "Liabilities")
    add(LIAB_CURR_TAGS, "liabilities_current", "Liabilities Current")
    add(EQUITY_TAGS, "equity", "Equity")
    add(CASH_TAGS, "cash", "Cash")
    add(RECEIVABLES_TAGS, "accounts_receivable", "AR")
    add(INVENTORY_TAGS, "inventory", "Inventory")
    add(DEBT_TAGS, "long_term_debt", "Debt")
    add(CAPEX_TAGS, "capex", "CapEx")
    add(OPER_CASHFLOW_TAGS, "operating_cf", "Op Cash Flow")
    add(INV_CASHFLOW_TAGS, "investing_cf", "Inv Cash Flow")
    add(FIN_CASHFLOW_TAGS, "financing_cf", "Fin Cash Flow")
    add(EMPLOYEE_TAGS, "employees", "Employees")
    # ------ Merge Quarterly ------
    df_q = quarts[0]
    for d in quarts[1:]:
        df_q = df_q.merge(d, on=["fy", "fp", "start", "end", "frequency"], how="outer")
    # ------ Merge Annual ------
    df_a = annuals[0]
    for d in annuals[1:]:
        df_a = df_a.merge(d, on=["fy", "fp", "start", "end", "frequency"], how="outer")
    # ------ Compute margins ------
    for df in (df_q, df_a):
        df["gross_margin_pct"] = df["gross_profit"] / df["revenue"]
        df["net_margin_pct"]   = df["net_income"]  / df["revenue"]
    # Keep only last N quarters for quarterly
    df_q = df_q.sort_values("end")
    if last_n_quarters:
        df_q = df_q.tail(last_n_quarters)
    
    # ------ Combine into one long-format DF ------
    df = pd.concat([df_q, df_a], ignore_index=True).sort_values(["fy", "fp", "start", "end", "frequency"])
    return df.reset_index(drop=True)


# Merge quarterly CSV files for a list of tickers
def merge__data(tickers, base_path, boycotted_tickers=None):
    """
    Merge quarterly CSV files for a list of tickers.
    
    Parameters:
        tickers (list): List of ticker symbols (e.g. ["COKE", "SBUX", "BROS"])
        base_path (str): Path to your data folder (up to /data)
        boycotted_tickers (list): Optional list of tickers that are boycotted. 
                                  If None, all are treated as control.
    """
    all_dfs = []
    boycotted_tickers = [t.upper() for t in (boycotted_tickers or [])]
    
    for ticker in tickers:
        ticker_lower = ticker.lower()
        is_boycotted = ticker.upper() in boycotted_tickers
        folder_type = "boycott_target" if is_boycotted else "control_group"
        
        #file_path = os.path.join(base_path, folder_type, ticker_lower, f"{ticker_lower}_quarterly.csv")
        file_path = os.path.join(base_path, folder_type, ticker_lower, f"{ticker_lower}.csv")
        
        
        if not os.path.exists(file_path):
            print(f"⚠️ File not found for {ticker}: {file_path}")
            continue
        
        df = pd.read_csv(file_path)
        
        # Add metadata columns only if they don't exist
        if "ticker" not in df.columns:
            df.insert(0, "ticker", ticker.upper())
        else:
            df["ticker"] = ticker.upper()

        if "boycotted" not in df.columns:
            df.insert(0, "boycotted", 1 if is_boycotted else 0)
        else:
            df["boycotted"] = 1 if is_boycotted else 0
        
        all_dfs.append(df)
        print(f"✅ Loaded {ticker}")
    
    if not all_dfs:
        raise ValueError("No valid CSV files found for the given tickers.")
    
    merged_df = pd.concat(all_dfs, ignore_index=True)
    
    # Sort if fiscal year exists
    if "fy" in merged_df.columns:
        merged_df = merged_df.sort_values(by=["ticker", "fy"])
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    #output_filename = f"merged_dataset_{timestamp}.csv"
    output_filename = f"merged_dataset_raw_{timestamp}.csv"
    output_path = os.path.join(base_path, output_filename)
    merged_df.to_csv(output_path, index=False)
    
    print(f"\nMerged dataset saved to: {output_path}")
    return merged_df

