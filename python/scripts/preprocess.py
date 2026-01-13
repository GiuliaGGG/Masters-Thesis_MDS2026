from python.imports import *
from python.config import *
from python.scripts.functions.preprocessing import *
from python.scripts.functions.scraping import *
from python.scripts.functions.tagging import *

def preprocess():
    # -----------------
    # Load raw data
    # -----------------
    input_path = os.path.join(DATA_RAW, "financials.csv")
    output_path = os.path.join(DATA_PROCESSED, "financials_clean.csv")

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
    # Save processed data
    # -----------------

    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    preprocess()


