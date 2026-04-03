from rag.search import search_docs

def search_documents(query: str) -> str:
    results = search_docs(query)

    if not results:
        return "No relevant documents found."

    return f"Here is what I found: {results[:2000]}"