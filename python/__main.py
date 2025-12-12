from python.imports import *
from python.config import *
from python.scraping import *
from python.tagging import *

def main():
    # -----------------------------------
    # Flatten all tags from all tag groups
    # -----------------------------------
    tags = sorted({
        tag
        for tag_list in TAG_GROUPS.values()
        for tag in tag_list
    })

    # -----------------
    # Collect SEC data
    # -----------------
    df_raw = collect_concepts_long(tickers, tags)

    # -----------------
    # Add semantic label
    # -----------------
    df = add_label_from_source_tag(df_raw)

    # -----------------
    # Save & inspect
    # -----------------
    output_path = (
        "./data/raw/financials.csv"
    )

    df.to_csv(output_path, index=False)

    print(df.head())

if __name__ == "__main__":
    main()

