# chart_generator.py
import pandas as pd
import plotly.express as px


def clean_numeric(df: pd.DataFrame):
    """
    Convert numeric-looking columns to real numeric dtype.
    Invalid values become NaN.
    """
    cleaned = df.copy()

    for col in cleaned.columns:
        if cleaned[col].dtype == object:
            # Try converting to numeric
            converted = pd.to_numeric(cleaned[col], errors="coerce")

            # Only accept conversion if at least 80% values are valid numbers
            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.8:
                cleaned[col] = converted

    return cleaned


def detect_column_roles(df: pd.DataFrame):
    """
    Return two lists: categorical columns and numeric columns.
    Uses cleaned numeric detection.
    """
    numeric_cols = []
    categorical_cols = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    return categorical_cols, numeric_cols


def choose_chart_type(df, categorical_cols, numeric_cols):
    """
    Chart selection rules:
    - If 1 categorical + 1 numeric → bar
    - If few categories (<6) → pie
    - If datetime + numeric → line
    - Multi-line only if numeric columns are clean & consistent
    """

    # CASE 1 — Simple categorical → numeric → BAR or PIE
    if len(categorical_cols) == 1 and len(numeric_cols) == 1:
        cat = categorical_cols[0]
        num = numeric_cols[0]

        if df[cat].nunique() <= 6:
            return "pie", cat, num

        return "bar", cat, num

    # CASE 2 — datetime + numeric → LINE
    for col in categorical_cols:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return "line", col, numeric_cols[0]

    # CASE 3 — MULTI LINE (strict requirements)
    if len(numeric_cols) >= 2:
        # All numeric columns must share the same dtype
        dtypes = {df[col].dtype for col in numeric_cols}
        if len(dtypes) == 1 and df.shape[0] >= 5:
            return "multi_line", None, numeric_cols

    # CASE 4 — fallback to bar on first categorical/numeric pair
    if categorical_cols and numeric_cols:
        return "bar", categorical_cols[0], numeric_cols[0]

    return None, None, None


def generate_chart(df: pd.DataFrame):
    """
    Main entrypoint:
    - Clean numeric columns
    - Detect roles
    - Pick chart type
    - Build a Plotly Figure
    """

    if df.empty:
        return None, "No data."

    df = clean_numeric(df)
    categorical_cols, numeric_cols = detect_column_roles(df)
    chart_type, x, y = choose_chart_type(df, categorical_cols, numeric_cols)

    if chart_type is None:
        return None, "No suitable chart type found."

    # BUILD CHARTS SAFELY
    if chart_type == "bar":
        fig = px.bar(df, x=x, y=y, title=f"{y} by {x}")

    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, title=f"{y} over {x}")

    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y, title=f"{y} distribution by {x}")

    elif chart_type == "multi_line":
        # Avoid wide-form issues by melting numerics if needed
        melted = df[numeric_cols].reset_index().melt(id_vars="index")
        fig = px.line(
            melted,
            x="index",
            y="value",
            color="variable",
            title="Multi-Series Trend",
        )

    else:
        return None, "Unsupported chart type."

    return fig, None
