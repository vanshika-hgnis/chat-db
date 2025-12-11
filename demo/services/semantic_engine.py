# services/semantic_engine.py
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# small + fast embedding model
_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# canonical semantic concepts
DIMENSION_CONCEPTS = [
    "name",
    "type",
    "category",
    "plan",
    "code",
    "product",
    "customer",
    "vendor",
    "employee",
    "tax",
    "item",
]

METRIC_CONCEPTS = [
    "amount",
    "value",
    "rate",
    "percentage",
    "total",
    "quantity",
    "price",
    "cost",
]

DATE_CONCEPTS = ["date", "time", "month", "year"]


def _embed(texts):
    return _MODEL.encode(texts, normalize_embeddings=True)


_DIM_EMB = _embed(DIMENSION_CONCEPTS)
_MET_EMB = _embed(METRIC_CONCEPTS)
_DATE_EMB = _embed(DATE_CONCEPTS)


def classify_columns(df: pd.DataFrame):
    """
    Returns semantic roles for columns:
    dimensions, metrics, dates, flags
    """

    dims, metrics, dates, flags = [], [], [], []

    col_embs = _embed(df.columns.tolist())

    for i, col in enumerate(df.columns):
        sim_dim = util.cos_sim(col_embs[i], _DIM_EMB).max().item()
        sim_met = util.cos_sim(col_embs[i], _MET_EMB).max().item()
        sim_date = util.cos_sim(col_embs[i], _DATE_EMB).max().item()

        if sim_date > 0.6:
            dates.append(col)
        elif sim_met > sim_dim and pd.api.types.is_numeric_dtype(df[col]):
            metrics.append(col)
        elif df[col].nunique() <= 3:
            flags.append(col)
        else:
            dims.append(col)

    return {
        "dimensions": dims,
        "metrics": metrics,
        "dates": dates,
        "flags": flags,
    }
