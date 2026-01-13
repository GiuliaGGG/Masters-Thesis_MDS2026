from python.imports import *
from python.config import *

def add_label_from_source_tag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'label' column to df based on which TAG GROUP the source_tag belongs to.
    """

    # Reverse map: tag -> label
    tag_to_label = {
        tag: label
        for label, tags in TAG_GROUPS.items()
        for tag in tags
    }

    df = df.copy()
    df["label"] = df["source_tag"].map(tag_to_label)

    return df

