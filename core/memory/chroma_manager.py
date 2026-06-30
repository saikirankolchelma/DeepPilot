import os
import chromadb
from chromadb.config import Settings
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv

load_dotenv()

class LocalOllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model_name = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        try:
            try:
                from langchain_ollama import OllamaEmbeddings
            except ImportError:
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

    def _get_collection_safe(self, collection_name: str):
        return self.client.get_or_create_collection(name=collection_name, embedding_function=self.embedding_fn)

    def add_to_memory(self, collection_name: str, doc_id: str, text: str, metadata: dict = None):
        collection = self._get_collection_safe(collection_name)
        try:
            collection.add(
                documents=[text],
                metadatas=[metadata] if metadata else None,
                ids=[doc_id]
            )
        except Exception as e:
            if "dimension" in str(e).lower() or "expecting embedding with dimension" in str(e).lower():
                # Stale collection from old Gemini embedding model (3072 dims vs 768 dims). Delete and recreate.
                self.client.delete_collection(name=collection_name)
                collection = self._get_collection_safe(collection_name)
                collection.add(
                    documents=[text],
                    metadatas=[metadata] if metadata else None,
                    ids=[doc_id]
                )
            else:
                raise e

    def search_memory(self, collection_name: str, query: str, n_results: int = 3):
        collection = self._get_collection_safe(collection_name)
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except Exception as e:
            if "dimension" in str(e).lower() or "expecting embedding with dimension" in str(e).lower():
                self.client.delete_collection(name=collection_name)
                collection = self._get_collection_safe(collection_name)
                return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            raise e
