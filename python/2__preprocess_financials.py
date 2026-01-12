from python.imports import *
from python.config import *
from python.scraping import *
from python.tagging import *
from python.preprocessing import *

def preprocess_financials():
    # -----------------
    # Load raw data
    # -----------------
    input_path = "../data/raw/financials_batch_3.csv"

    df = pd.read_csv(input_path)

     # -----------------
    # Add year and quarter
    # -----------------
    df = add_year_quarter(df)
    # -----------------
    # Quarterly filter + interval_days
    # -----------------
    df = filter_quarterly_intervals(df)

    # -----------------
    # Collapse frame duplicates
    # -----------------
    df = collapse_duplicates_ignoring_frame(df)

    # -----------------
    # Deduplicate by latest filing
    # -----------------
    df = deduplicate_by_latest_filing(df)

    # -----------------
    # Dominant source tag
    # -----------------
    df = select_dominant_source_tag_with_fallback(df)

    # -----------------
    # Keep max interval when conflicts exist
    # -----------------
    df = keep_max_interval_observation(df)

    # -----------------
    # Save output
    # -----------------
    output_path = (
        "./data/processed/financials_preprocessed.csv"
    )

    df.to_csv(output_path, index=False)
    return df


if __name__ == "__preprocess__":
    preprocess_financials()


# %%
