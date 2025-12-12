from functions import *
from imports import *
from config import *

# check if the df gets generated
if __name__ == "__main__":
    TICKER = "MCD"  # replace with any ticker
    df = get_financials(TICKER, last_n_quarters=200)

    print(df)

    # Show all columns and shape
    print(df.columns)
    print(df.shape)