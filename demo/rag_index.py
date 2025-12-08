import os

os.environ["TORCH_DISABLE_TORCH_INDEXING"] = "1"


# rag_index.py
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


DATA_DIR = "data"
SCHEMA_JSON = os.path.join(DATA_DIR, "db_schema.json")
INDEX_PATH = os.path.join(DATA_DIR, "schema.index")
TEXTS_PATH = os.path.join(DATA_DIR, "schema_texts.json")

# small, fast model good enough for schema descriptions
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def build_index():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(SCHEMA_JSON):
        raise FileNotFoundError(
            f"{SCHEMA_JSON} not found. Run schema_scanner.scan_schema() first."
        )

    with open(SCHEMA_JSON, "r", encoding="utf-8") as f:
        schema = json.load(f)

    texts = [entry["text"] for entry in schema]

    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    embeddings = np.asarray(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine via normalized vectors
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    with open(TEXTS_PATH, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)

    print(f"FAISS index saved to {INDEX_PATH} (+ texts {TEXTS_PATH}).")


def load_index():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(TEXTS_PATH):
        raise FileNotFoundError(
            "Index or texts not found. Run build_index() once first."
        )

    index = faiss.read_index(INDEX_PATH)
    with open(TEXTS_PATH, "r", encoding="utf-8") as f:
        texts = json.load(f)
    return index, texts


def retrieve_schema_snippets(question: str, top_k: int = 5):
    index, texts = load_index()
    model = get_model()

    q_emb = model.encode([question], normalize_embeddings=True)
    q_emb = np.asarray(q_emb, dtype="float32")

    scores, idx = index.search(q_emb, top_k)
    idx_list = idx[0]

    snippets = [texts[i] for i in idx_list if i >= 0]
    return snippets
