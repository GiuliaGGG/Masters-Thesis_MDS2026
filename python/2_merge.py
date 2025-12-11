from imports import *
from functions import merge_data

# Example usage:
if __name__ == "__main__":
    base_path = "/Users/giuliamariapetrilli/Documents/GitHub/masters_thesis/data/raw"
boycotted = [
    "MCD",     # McDonald's (NYSE)
]

control_group = [
    "BROS",    # Dutch Bros Inc.
    "CMG",     # Chipotle Mexican Grill, Inc.
    "COST",    # Costco Wholesale Corporation
    "GIS",     # General Mills, Inc.
    "JNJ",     # Johnson & Johnson
    "MDLZ",    # Mondelez International, Inc.
    "NKE",     # Nike, Inc.
    "TGT",     # Target Corporation
    "TRIP",    # Tripadvisor, Inc.
    "WEN",     # The Wendy’s Company
    "WMT",     # Walmart Inc.
]
tickers = boycotted + control_group

merged_df = merge_data(tickers, base_path, boycotted_tickers=boycotted)
print(merged_df.head())
