import requests
import json

# ============================================================
# 1. LOAD THE SEC JSON (McDonald's CIK 0000063908)
# ============================================================
# CIK0000063908 mcdonals
url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000063908.json"
url_revenue = "https://data.sec.gov/api/xbrl/companyconcept/CIK0000063908/us-gaap/Revenues.json"
headers = {"User-Agent": "Giulia Petrilli giuliapetrilli2000@gmail.com"}  # SEC requires this

print("Downloading SEC JSON...")
data = requests.get(url, headers=headers).json()
data_revenue = requests.get(url_revenue, headers=headers).json()
print("Download complete!")


# ============================================================
# 2. SEARCH FOR TAG NAMES CONTAINING A KEYWORD
#    Example: search_tags("revenue")
# ============================================================

def search_tags(keyword, data):
    keyword = keyword.lower()
    results = []
    
    for taxonomy, items in data.items():
        if not isinstance(items, dict):
            continue

        for tag in items.keys():
            if keyword in tag.lower():
                results.append(f"{taxonomy}.{tag}")

    return results


# ============================================================
# 3. GET FACTS FOR A SPECIFIC TAG
#    Example: get_facts("us-gaap.Revenues")
# ============================================================

def get_facts(full_tag, data):
    try:
        taxonomy, tag = full_tag.split(".")
        return data[taxonomy][tag]["units"]
    except Exception:
        return None


# ============================================================
# 4. SEARCH FOR A NUMERIC VALUE ANYWHERE IN THE JSON
#    Example: find_value(27000000)
# ============================================================

def find_value_contains(query, data):
    query = str(query).lower()      # normalize search term
    matches = []

    def search(obj, path="root"):
        if isinstance(obj, dict):
            for k, v in obj.items():
                search(v, f"{path}.{k}")

        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                search(v, f"{path}[{i}]")

        else:
            # Convert all leaf values to string to allow partial matching
            try:
                text = str(obj).lower()
                if query in text:
                    matches.append((path, obj))
            except Exception:
                pass  # skip values that cannot be stringified

    search(data)
    return matches



# ============================================================
# 5. EXAMPLE USAGE (you can comment these out)
# ============================================================

print("\nEXAMPLE SEARCHES\n")

# Search for tags containing a keyword
print("Tags containing 'Revenues")
print(search_tags("Revenues", data))
print(search_tags("Revenues", data_revenue))

# Fetch facts for a tag
print("\nFacts for us-gaap.Revenues:")
revenue_facts = get_facts("us-gaap.Revenues", data)
revenue_facts = get_facts("us-gaap.Revenues", data_revenue)
print(json.dumps(revenue_facts, indent=2))

# Search for a specific numeric value
print("\nSearching for value :")
find_value_contains("66151", data)
find_value_contains('66151', data_revenue)

find_value_contains("19071700000", data)
find_value_contains('19071700000', data_revenue)



import time
from typing import Dict, List
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os


# ---------- CONFIG ----------
UA = {"User-Agent": "Giulia Petrilli giuliapetrilli2000@gmail.com"}
BASE = "https://data.sec.gov/api" 



# --- TAG GROUPS ---
REVENUE_TAGS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueNet"
]
GROSS_PROFIT_TAGS = ["GrossProfit"]
COST_TAGS = ["CostOfRevenue", "CostOfGoodsAndServicesSold"]
NET_INCOME_TAGS = ["NetIncomeLoss"]

OPERATING_EXP_TAGS = ["OperatingExpenses", "SellingGeneralAndAdministrativeExpenses"]
R_AND_D_TAGS = ["ResearchAndDevelopmentExpense"]
DEPR_AMORT_TAGS = ["DepreciationAndAmortization", "AmortizationExpense"]
INTEREST_EXP_TAGS = ["InterestExpense"]
INTEREST_INC_TAGS = ["InterestIncome"]
INCOMEBEFORETAX_TAGS = ["IncomeBeforeTax"]
TAX_TAGS = ["IncomeTaxExpenseBenefit", "ProvisionForIncomeTaxes"]

EPS_BASIC_TAGS = ["EarningsPerShareBasic"]
EPS_DILUTED_TAGS = ["EarningsPerShareDiluted"]
SHARES_BASIC_TAGS = ["WeightedAverageNumberOfSharesOutstandingBasic"]
SHARES_DILUTED_TAGS = ["WeightedAverageNumberOfDilutedSharesOutstanding"]

ASSETS_TAGS = ["Assets"]
ASSETS_CURR_TAGS = ["AssetsCurrent"]
LIAB_TAGS = ["Liabilities"]
LIAB_CURR_TAGS = ["LiabilitiesCurrent"]
EQUITY_TAGS = ["StockholdersEquity", "Equity"]
CASH_TAGS = ["CashAndCashEquivalentsAtCarryingValue"]
RECEIVABLES_TAGS = ["AccountsReceivableNetCurrent"]
INVENTORY_TAGS = ["InventoriesNet"]
DEBT_TAGS = ["LongTermDebt"]

CAPEX_TAGS = ["CapitalExpenditures"]
OPER_CASHFLOW_TAGS = ["NetCashProvidedByOperatingActivities"]
INV_CASHFLOW_TAGS = ["NetCashUsedForInvestingActivities"]
FIN_CASHFLOW_TAGS = ["NetCashProvidedByFinancingActivities"]

EMPLOYEE_TAGS = ["NumberOfEmployees", "WeightedAverageNumberOfEmployees"]

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

# ---------- PARSING SERIES ----------
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
