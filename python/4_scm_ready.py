from python.imports import *
from python.config import *
from python.scraping import *
from python.tagging import *
from python.preprocessing import *

data = pd.read_csv("./data/processed/data.csv")

df_netinc = restrict_to_observed_outcome(
    data,
    outcome_col="net_income"
)

df_revenue = restrict_to_observed_outcome(
    data,
    outcome_col="revenue"
)
df_revenue_imputed = complete_and_impute_quarters(
    df_revenue,
    unit_col="ticker",
    time_col="time",
    value_col="revenue",
    method="locf",
    full_grid="global"
)
# confirm balancedness
balanced_check = (
    df_revenue_imputed
    .groupby("ticker")["time"]
    .nunique()
    .describe()
)
print(balanced_check)

df_revenue_imputed["revenue"] = (
    df_revenue_imputed
    .groupby("ticker")["revenue"]
    .apply(lambda s: s.ffill().bfill())
    .reset_index(level=0, drop=True)
)

# confirm no missing revenue  
print(df_revenue_imputed["revenue"].isna().sum())

# how much was imputed
print(df_revenue_imputed["revenue_imputed"].mean())
df_revenue_imputed.to_csv(
    "./data/processed/revenue_imputed.csv",
    index=False
)