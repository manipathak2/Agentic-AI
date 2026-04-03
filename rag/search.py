import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Try to load index and docs, handle missing files gracefully
index = None
docs = []
metadata = []

try:
    if os.path.exists("rag/index.faiss"):
        index = faiss.read_index("rag/index.faiss")
    if os.path.exists("rag/docs.pkl"):
        with open("rag/docs.pkl", "rb") as f:
            docs, metadata = pickle.load(f)
except Exception as e:
    print(f"Warning: Could not load RAG index: {e}")
    index = None

def search_docs(query, k=3):
    if index is None or not docs:
        return "Document search is not available. No documents have been indexed yet."

    try:
        query_vector = model.encode([query])
        distances, indices = index.search(query_vector, k)

        results = []
        for i in indices[0]:
            if i < len(docs):
                results.append(docs[i])

        return "\n".join(results) if results else "No relevant documents found."
    except Exception as e:
        return f"Error searching documents: {e}"