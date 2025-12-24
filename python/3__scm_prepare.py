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

    df = add_scm_time_index(df)
    df = resolve_collisions_prefer_10q_then_latest_end(df)
    df = refine_estimation_window(df)
    df = drop_chronically_sparse_donors(df)
    df = pivot_wide(df)

    df = complete_scm_time_grid(
        df=df,
        unit_col="ticker",
        time_col="time"
    )

    df = impute_all_numeric_within_unit(
        df=df,
        unit_col="ticker",
        time_col="time",
        exclude_cols=["ticker"],  # treatment indicator (do NOT impute)
        method="both"
    )
  
    vars_to_standardize = [
        "cost",
        "depr_amort",
        "eps_basic",
        "eps_diluted",
        "gross_profit",
        "interest_exp",
        "net_income",
        "operating_exp",
        "revenue",
        "shares_basic",
        "shares_diluted",
        "tax"
    ]

    df = standardize_by_period0(
        df=df,
        unit_col="ticker",
        time_col="time",
        cols=vars_to_standardize,
        method="ratio"   
    )



    # -----------------
    # Save output
    # -----------------
    output_path = (
        "./data/processed/data_standardized.csv"
    )

    df.to_csv(output_path, index=False)



    return df


if __name__ == "__scm_prepare__":
    scm_prepare()
