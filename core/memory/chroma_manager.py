import os
import chromadb
from chromadb.config import Settings
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv

load_dotenv()

class LocalOllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model_name = os.getenv("EMBEDDING_MODEL", "deepseek-r1:8b")
        try:
            from langchain_community.embeddings import OllamaEmbeddings
            self.embeddings = OllamaEmbeddings(model=self.model_name, base_url=self.base_url)
        except Exception:
            self.embeddings = None
        
    def __call__(self, input: Documents) -> Embeddings:
        if self.embeddings:
            try:
                return self.embeddings.embed_documents(input)
            except Exception:
                pass
        # Fallback to local SentenceTransformers if Ollama embeddings fail
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        st_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        return st_fn(input)

class ChromaManager:
    def __init__(self):
        db_path = os.getenv("CHROMA_DB_PATH", "./memory_store")
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Use Local Ollama / SentenceTransformer embeddings
        self.embedding_fn = LocalOllamaEmbeddingFunction()
        
        # Initialize collections
        self.episodic_memory = self.client.get_or_create_collection(
            name="episodic_memory", 
            embedding_function=self.embedding_fn
        )
        self.semantic_memory = self.client.get_or_create_collection(
            name="semantic_memory", 
            embedding_function=self.embedding_fn
        )
        self.short_term_memory = self.client.get_or_create_collection(
            name="short_term_memory", 
            embedding_function=self.embedding_fn
        )

    def add_to_memory(self, collection_name: str, doc_id: str, text: str, metadata: dict = None):
        collection = self.client.get_collection(name=collection_name, embedding_function=self.embedding_fn)
        collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else None,
            ids=[doc_id]
        )

    def search_memory(self, collection_name: str, query: str, n_results: int = 3):
        collection = self.client.get_collection(name=collection_name, embedding_function=self.embedding_fn)
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
