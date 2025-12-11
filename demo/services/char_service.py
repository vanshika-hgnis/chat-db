# services/chart_service.py

import pandas as pd
import plotly.express as px

from services.semantic_engine import classify_columns
from services.question_intent import detect_intent
from utils.numeric_cleaner import clean_numeric_columns


# -----------------------------------------------------
# Aggregation Picker
# -----------------------------------------------------
def pick_aggregation(metric_name: str):
    name = metric_name.lower()

    if "rate" in name or "%" in name:
        return "avg"
    if "price" in name or "cost" in name:
        return "avg"
    if "count" in name:
        return "count"

    # Default for business metrics
    return "sum"


# -----------------------------------------------------
# Chart Service – Vanna-Style Smart Chart Builder
# -----------------------------------------------------
def generate_chart(df: pd.DataFrame, question: str):
    """
    Create question-aware chart based on semantic column roles.
    Returns (fig, error_message)
    """

    # ------------------------
    # 0. Empty Data Check
    # ------------------------
    if df.empty:
        return None, "No data available to plot."

    # ------------------------
    # 1. Clean numerics
    # ------------------------
    df = clean_numeric_columns(df)

    # ------------------------
    # 2. Semantic Classification
    # ------------------------
    sem = classify_columns(df)
    dims = sem["dimensions"]
    metrics = sem["metrics"]
    dates = sem["dates"]
    flags = sem["flags"]

    # ------------------------
    # 3. Determine User Intent
    # ------------------------
    intent = detect_intent(question)

    # ------------------------
    # 4. Validate semantic structure
    # ------------------------
    if not dims and not dates:
        return None, "No suitable dimension column found for chart."

    if not metrics:
        return None, "No numeric or aggregatable column found for chart."

    # --------------------------------------------------------
    # 5. Select X-axis and Y-axis based on intent
    # --------------------------------------------------------

    # PRIORITY 1 — Trend → use a date column if available
    if intent == "trend" and dates:
        x = dates[0]
    else:
        # use the first semantic dimension
        x = dims[0] if dims else dates[0]

    # Choose primary metric
    y = metrics[0]
    agg = pick_aggregation(y)

    # --------------------------------------------------------
    # 6. Aggregation Logic
    # --------------------------------------------------------
    if agg == "sum":
        chart_df = df.groupby(x, as_index=False)[y].sum()
        y_label = f"Total {y}"

    elif agg == "avg":
        chart_df = df.groupby(x, as_index=False)[y].mean()
        y_label = f"Average {y}"

    elif agg == "count":
        chart_df = df.groupby(x, as_index=False)[y].count()
        y_label = f"Count of {y}"

    else:
        chart_df = df
        y_label = y

    # --------------------------------------------------------
    # 7. Smart Chart Type Selection
    # --------------------------------------------------------

    # Trend line for date-based intent
    if intent == "trend" and dates:
        chart_type = "line"

    # Pie chart for distribution questions
    elif intent == "distribution":
        chart_type = "pie"

    # Correlation → scatter (if at least 2 metrics)
    elif intent == "correlation" and len(metrics) >= 2:
        chart_type = "scatter"

    # Default → bar comparison
    else:
        chart_type = "bar"

    # --------------------------------------------------------
    # 8. Render Chart
    # --------------------------------------------------------

    title = f"{y_label} by {x}".replace("_", " ").title()

    if chart_type == "pie":
        fig = px.pie(chart_df, names=x, values=y, title=title)

    elif chart_type == "line":
        fig = px.line(chart_df, x=x, y=y, title=title)

    elif chart_type == "scatter":
        second_metric = metrics[1]
        fig = px.scatter(chart_df, x=y, y=second_metric, title="Correlation Plot")

    else:  # default bar chart
        fig = px.bar(chart_df, x=x, y=y, text=y, title=title)
        fig.update_traces(textposition="outside")

    fig.update_layout(
        xaxis_title=x.replace("_", " ").title(),
        yaxis_title=y_label,
        title=title,
    )

    return fig, None
