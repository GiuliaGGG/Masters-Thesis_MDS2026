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
DEBT_TAGS = ["LongTermDebt"]


# --- UNIT SCALE MAPPING ---
UNIT_SCALE = {
    "USD": 1,
    "USD$": 1,
    "USD (in dollars)": 1,
    "USD (in thousands)": 1_000,
    "USD (in millions)": 1_000_000,
    "USD (in billions)": 1_000_000_000,
}
