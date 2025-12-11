from functions import get_financials
from imports import *

# check if the df gets generated
if __name__ == "__main__":
    TICKER = "WEN"  # replace with any ticker
    df = get_financials(TICKER, last_n_quarters=200)

    print(df)

    # Show all columns and shape
    print(df.columns)
    print(df.shape)