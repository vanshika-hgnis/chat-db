# utils/numeric_cleaner.py
import pandas as pd


def clean_numeric_columns(df: pd.DataFrame):
    out = df.copy()

    for col in out.columns:
        if out[col].dtype == object:
            converted = pd.to_numeric(out[col], errors="coerce")
            if converted.notna().mean() > 0.7:
                out[col] = converted

    return out
