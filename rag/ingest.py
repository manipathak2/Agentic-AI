from sentence_transformers import SentenceTransformer
import faiss
import os
import pickle
from PyPDF2 import PdfReader

model = SentenceTransformer("all-MiniLM-L6-v2")

docs = []
metadata = []

DATA_PATH = "rag/data"

for file in os.listdir(DATA_PATH):
    if file.endswith(".pdf"):
        reader = PdfReader(os.path.join(DATA_PATH, file))

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                docs.append(text)
                metadata.append(f"{file} - page {page_num}")

# Convert to embeddings
embeddings = model.encode(docs)

# Store in FAISS
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save
faiss.write_index(index, "rag/index.faiss")

with open("rag/docs.pkl", "wb") as f:
    pickle.dump((docs, metadata), f)

print("✅ Documents indexed")