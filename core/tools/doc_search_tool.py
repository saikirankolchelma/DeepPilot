from langchain.tools import tool

@tool
def search_documentation(query: str, library_name: str = "python") -> str:
    """
    Searches documentation for a specific library.
    """
    # In a full implementation, this would query a vector store (ChromaDB) 
    # containing scraped documentation or use a web API like Tavily.
    # For now, it returns a placeholder instructing the agent that the search failed
    # so it relies on its internal knowledge.
    return f"Search capability for {library_name} docs is currently offline. Please rely on your internal knowledge."
