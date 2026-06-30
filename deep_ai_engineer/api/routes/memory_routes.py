from fastapi import APIRouter
from memory.chroma_manager import ChromaManager
from pydantic import BaseModel

router = APIRouter()
db = ChromaManager()

class SearchQuery(BaseModel):
    query: str
    collection: str = "semantic_memory"
    k: int = 3

@router.post("/search")
async def search_memory(request: SearchQuery):
    results = db.search_memory(request.collection, request.query, request.k)
    return {"results": results}
