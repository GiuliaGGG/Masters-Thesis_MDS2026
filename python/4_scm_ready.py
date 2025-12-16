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
