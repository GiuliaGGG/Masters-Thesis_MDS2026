# %%
# ---------- CONFIG ----------
UA = {"User-Agent": "Giulia Petrilli giuliapetrilli2000@gmail.com"}
BASE = "https://data.sec.gov/api" 


# ===============================
# US-GAAP TAG GROUPS 
# ===============================

# ---- Revenue ----
revenue_tags = [
    "Revenues",
    "SalesRevenueNet",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueGoodsNet",
    "SalesRevenueServicesNet",
    "SalesRevenueNetOfReturnsAndAllowances",
    "OperatingRevenues",
    "InterestAndDividendIncomeOperating",
]

# ---- Cost of Revenue / COGS ----
cost_tags = [
    "CostOfRevenue",
    "CostOfGoodsAndServicesSold",
    "CostOfGoodsSold",
    "CostOfServices",
]

# ---- Gross Profit ----
gross_profit_tags = [
    "GrossProfit",
]

# ---- Operating Expenses ----
operating_exp_tags = [
    "OperatingExpenses",
    "SellingGeneralAndAdministrativeExpenses",
    "GeneralAndAdministrativeExpense",
    "SellingAndMarketingExpense",
    "AdvertisingExpense",
]

# ---- Research & Development ----
r_and_d_tags = [
    "ResearchAndDevelopmentExpense",
    "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
]

# ---- Depreciation & Amortization ----
depr_amort_tags = [
    "DepreciationAndAmortization",
    "Depreciation",
    "AmortizationExpense",
    "DepreciationAmortizationAndAccretionNet",
]

# ---- Interest Expense ----
interest_exp_tags = [
    "InterestExpense",
    "InterestExpenseNet",
    "InterestAndDebtExpense",
]

# ---- Income Taxes ----
tax_tags = [
    "IncomeTaxExpenseBenefit",
    "ProvisionForIncomeTaxes",
    "IncomeTaxesPaid",
]

# ---- Net Income ----
net_income_tags = [
    "NetIncomeLoss",
    "ProfitLoss",
    "NetIncomeLossAttributableToParent",
    "IncomeLossFromContinuingOperations",
    "IncomeLossFromContinuingOperationsAttributableToParent",
]

# ---- Earnings Per Share ----
eps_basic_tags = [
    "EarningsPerShareBasic",
    "EarningsPerShareBasicContinuingOperations",
]

eps_diluted_tags = [
    "EarningsPerShareDiluted",
    "EarningsPerShareDilutedContinuingOperations",
]

# ---- Shares Outstanding ----
shares_basic_tags = [
    "WeightedAverageNumberOfSharesOutstandingBasic",
    "WeightedAverageNumberOfSharesOutstanding",
]

shares_diluted_tags = [
    "WeightedAverageNumberOfDilutedSharesOutstanding",
]

# ---- Assets ----
assets_tags = [
    "Assets",
]

assets_curr_tags = [
    "AssetsCurrent",
]

# ---- Liabilities ----
liab_tags = [
    "Liabilities",
]

liab_curr_tags = [
    "LiabilitiesCurrent",
]

# ---- Equity ----
equity_tags = [
    "StockholdersEquity",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    "Equity",
]

# ---- Cash ----
cash_tags = [
    "CashAndCashEquivalentsAtCarryingValue",
    "CashCashEquivalentsAndShortTermInvestments",
]

# ---- Receivables ----
receivables_tags = [
    "AccountsReceivableNetCurrent",
    "ReceivablesNetCurrent",
]

# ---- Debt ----
debt_tags = [
    "LongTermDebt",
    "LongTermDebtNoncurrent",
    "LongTermBorrowings",
]

TAG_GROUPS = {
        "revenue": revenue_tags,
        "cost": cost_tags,
        "gross_profit": gross_profit_tags,
        "operating_exp": operating_exp_tags,
        "r_and_d": r_and_d_tags,
        "depr_amort": depr_amort_tags,
        "interest_exp": interest_exp_tags,
        "tax": tax_tags,
        "net_income": net_income_tags,
        "eps_basic": eps_basic_tags,
        "eps_diluted": eps_diluted_tags,
        "shares_basic": shares_basic_tags,
        "shares_diluted": shares_diluted_tags,
        "assets": assets_tags,
        "assets_curr": assets_curr_tags,
        "liab": liab_tags,
        "liab_curr": liab_curr_tags,
        "equity": equity_tags,
        "cash": cash_tags,
        "receivables": receivables_tags,
        "debt": debt_tags,
    }

# ---- For fetching all relevant firms ----

#batch_1
#tickers = [
#    'MCD',     # McDonald's Corporation
#
#    "BROS",    # Dutch Bros Inc.
#    "CMG",     # Chipotle Mexican Grill, Inc.
#    "COST",    # Costco Wholesale Corporation
#    "GIS",     # General Mills, Inc.
 #   "JNJ",     # Johnson & Johnson
#    "MDLZ",    # Mondelez International, Inc.
#    "NKE",     # Nike, Inc.
#    "TGT",     # Target Corporation
#    "TRIP",    # Tripadvisor, Inc.
#    "WEN",     # The Wendy’s Company
#    "WMT",     # Walmart Inc.
#]

tickers = [
    'MCD',     # McDonald's Corporation
    "BROS",    # Dutch Bros Inc.
    "CMG",     # Chipotle Mexican Grill, Inc.
    "COST",    # Costco Wholesale Corporation
    "GIS",     # General Mills, Inc.
    "MDLZ",    # Mondelez International, Inc.
    "TGT",     # Target Corporation
    "WEN",     # The Wendy’s Company
    #"SBUX",    # Starbucks Corporation
    "JACK",    # Jack in the Box Inc.
    "WING",    # Wingstop Inc.
    "LOCO",    # El Pollo Loco Holdings, Inc.
    "SHAK",    # Shake Shack Inc.
    #"CAKE",    # The Cheesecake Factory Incorporated
    "TXRH",   # Texas Roadhouse, Inc.
    "DRI",    # Darden Restaurants, Inc.
    "BLMN",    # Bloomin' Brands, Inc.
    "SG",    # The Scotts Miracle-Gro Company
    "CAVA",    # CAVA Group, Inc.
    "NDLS",    # Noodles & Company
    "FWRG",   # Fiesta Restaurant Group, Inc.
    "DNUT",   # Dunkin' Brands Group, Inc.
    "CASY",   # Casey's General Stores, Inc.
    "ARKO",
    "MAR",     # Marriott International, Inc.
    "HLT",     # Hilton Worldwide Holdings Inc.
    "BBWI",    # Bath & Body Works, Inc.
    "GPS",     # The Gap, Inc.
    "HD",      # The Home Depot, Inc.
    "LOW",     # Lowe's Companies, Inc.
    "LEVI",    # Levi Strauss & Co.
    "NFLX",  # Netflix, Inc.
    "UBER",  # Uber Technologies, Inc.
]

# # batch_4 recent
# tickers = [
#     "MCD",     # McDonald's Corporation
#     "PZZA",    # Papa John's International, Inc.
#     "YUM",     # Yum! Brands, Inc.
#     "QSR",     # Restaurant Brands International Inc.
#      "DPZ",     # Domino's Pizza, Inc.
#      "DIS",   # The Walt Disney Company
#      "COKE",    # Coca-Cola Company
#      "PEP",     # PepsiCo, Inc.
#  ]

# define boycott parameters
BOYCOTTED_FIRM = 'MCD'
BOYCOTT_START =  '2024-03-31' # first available instance where you can see the effect of the boycott calls in 2025-11-05. The 2024 Q4 is imputed and not present yet at this stage. This is corrected further on. 

