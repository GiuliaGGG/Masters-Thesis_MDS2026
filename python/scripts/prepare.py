from python.imports import *
from python.config import *
from python.scripts.functions.preprocessing import *
from python.scripts.functions.scraping import *
from python.scripts.functions.tagging import *

def prepare():
    # -----------------
    # Load raw data
    # -----------------
    input_path = os.path.join(DATA_PROCESSED, "financials_clean.csv")
    output_path = os.path.join(OUTPUTS, "data.csv")

    df = pd.read_csv(input_path)

    df = add_scm_time_index(df)

     # -----------------
    # Define treatment (boycott)
    # -----------------
    df = define_boycotted(
        df,
        boycotted_firm=BOYCOTTED_FIRM,
        boycott_start=BOYCOTT_START
    )

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

    columns = [
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
    
    df = log_transform_vars(
    df,
    cols=columns
    )

    df = enforce_common_revenue_time_support(
        df=df,
        unit_col="ticker",
        time_col="time",
        revenue_col="revenue"
    )

    df = set_boycotted_from_time(
        df,
        start_time=8096,
        treated_ticker="MCD"
    )
    df = add_time_label_from_scm(df)

    # -----------------
    # Save output
    # -----------------  

    df.to_csv(output_path, index=False)

    return df


if __name__ == "__main__":
    prepare()
