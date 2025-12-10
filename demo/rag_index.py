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

EMBED_MODEL = "all-MiniLM-L6-v2"
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def build_index():
    with open(SCHEMA_JSON, "r", encoding="utf-8") as f:
        schema = json.load(f)

    texts = [entry["text"] for entry in schema]

    os.makedirs(DATA_DIR, exist_ok=True)
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    embeddings = np.asarray(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(TEXTS_PATH, "w", encoding="utf-8") as f:
        json.dump(texts, f)

    print("FAISS index built successfully.")


def load_index():
    index = faiss.read_index(INDEX_PATH)
    with open(TEXTS_PATH, "r", encoding="utf-8") as f:
        texts = json.load(f)
    return index, texts


def retrieve_schema_snippets(question: str, top_k: int = 15):
    index, texts = load_index()
    model = get_model()
    q_emb = model.encode([question], normalize_embeddings=True)
    q_emb = np.asarray(q_emb, dtype="float32")
    scores, idx = index.search(q_emb, top_k)
    return [texts[i] for i in idx[0] if i >= 0]
