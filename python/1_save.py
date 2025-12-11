from python.functions import get_financials
from python.imports import *
# Save financial data for a list of tickers to CSV files

if __name__ == "__main__":
    # --- USER INPUTS ---
    boycotted = True  # set to True for boycott targets, False for control group
    tickers = [
   'MCD',
]


 # <--- add any tickers you want here
    last_n_quarters = 200

    base_path = "/Users/giuliamariapetrilli/Documents/GitHub/masters_thesis/data"

    # --- LOOP THROUGH TICKERS ---
    for TICKER in tickers:
        print(f"\n===== Processing {TICKER.upper()} =====")

        try:
            # Fetch data
            df = get_financials(TICKER, last_n_quarters=last_n_quarters)
            if df.empty:
                print(f"⚠️ No data returned for {TICKER}. Skipping.")
                continue

            # Add metadata columns
            df.insert(0, 'ticker', TICKER.upper())
            df.insert(0, 'boycotted', int(boycotted))

             # Choose folder based on flag
            if boycotted:
                folder = f"{base_path}/with_start_date/boycott_target/{TICKER.lower()}"
            else:
                folder = f"{base_path}/with_start_date/control_group/{TICKER.lower()}"


            # Create folder if needed
            os.makedirs(folder, exist_ok=True)

            # Save file
            #output_path = f"{folder}/{TICKER.lower()}_quarterly.csv"
            output_path = f"{folder}/{TICKER.lower()}.csv"
            df.to_csv(output_path, index=False)

            # Show confirmation
            print(f"✅ Saved {TICKER} data to: {output_path}")
            print(f"   → Shape: {df.shape}")
            print(f"   → Columns: {list(df.columns)}")

        except Exception as e:
            print(f"❌ Error processing {TICKER}: {e}")
