import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
import pickle
import os


class SchemaEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.schema_map = []

    def embed_and_store(
        self, schema_list, index_path="faiss.index", map_path="schema_map.pkl"
    ):
        embeddings = self.model.encode(schema_list)
        self.index = faiss.IndexFlatL2(len(embeddings[0]))
        self.index.add(np.array(embeddings))

        self.schema_map = schema_list

        faiss.write_index(self.index, index_path)
        with open(map_path, "wb") as f:
            pickle.dump(schema_list, f)

    def load_index(self, index_path="faiss.index", map_path="schema_map.pkl"):
        self.index = faiss.read_index(index_path)
        with open(map_path, "rb") as f:
            self.schema_map = pickle.load(f)

    def search(self, query, top_k=5):
        embedding = self.model.encode([query])
        D, I = self.index.search(np.array(embedding), top_k)
        return [self.schema_map[i] for i in I[0]]
