from python.imports import *
from python.config import *
from python.scraping import *
from python.tagging import *
from python.preprocessing import *

def scm_prepare():
    # -----------------
    # Load raw data
    # -----------------
    input_path = (
        "./data/processed/financials_preprocessed.csv"
    )

    df = pd.read_csv(input_path)

    # -----------------
    # Define treatment (boycott)
    # -----------------
    df = define_boycotted(
        df,
        boycotted_firm=BOYCOTTED_FIRM,
        boycott_start=BOYCOTT_START
    )

    df = add_quarterly_time_index(df)
    df = resolve_collisions_prefer_10k_then_latest_end(df)


    # -----------------
    # Save output
    # -----------------
    output_path = (
        "./data/processed/data.csv"
    )

    df.to_csv(output_path, index=False)

    return df


if __name__ == "__scm_prepare__":
    scm_prepare()


