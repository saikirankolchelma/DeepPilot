from memory.chroma_manager import ChromaManager
import uuid

class MemoryRouter:
    def __init__(self):
        self.db = ChromaManager()

    def store_short_term(self, task_id: str, action: str, result: str):
        """Stores active workflow steps during an ongoing task."""
        doc_id = str(uuid.uuid4())
        text = f"Task ID: {task_id}\nAction: {action}\nResult: {result}"
        self.db.add_to_memory(
            collection_name="short_term_memory",
            doc_id=doc_id,
            text=text,
            metadata={"task_id": task_id, "type": "workflow_step"}
        )

    def store_episodic(self, task_id: str, summary: str, success: bool):
        """Stores the final result and summary of a completed workflow."""
        doc_id = str(uuid.uuid4())
        self.db.add_to_memory(
            collection_name="episodic_memory",
            doc_id=doc_id,
            text=summary,
            metadata={"task_id": task_id, "success": success}
        )

    def store_semantic(self, concept: str, explanation: str):
        """Stores reusable architectural knowledge or code patterns."""
        doc_id = str(uuid.uuid4())
        self.db.add_to_memory(
            collection_name="semantic_memory",
            doc_id=doc_id,
            text=explanation,
            metadata={"concept": concept}
        )

    def retrieve_relevant_context(self, query: str, collection_name: str = "semantic_memory", k: int = 3):
        """Retrieves top k relevant documents for a query."""
        results = self.db.search_memory(collection_name, query, n_results=k)
        # Extract just the texts for easier consumption by LLMs
        if results and 'documents' in results and len(results['documents']) > 0:
            return results['documents'][0]
        return []
