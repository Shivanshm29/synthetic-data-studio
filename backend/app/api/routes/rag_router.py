from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Any

from app.rag.rag_engine import RAGEngine

router = APIRouter(
    prefix="/rag",
    tags=["RAG Knowledge Base"],
)

rag_engine = RAGEngine.get_instance()


class RAGRetrieveRequest(BaseModel):
    prompt: str
    top_k: int = 2


class RAGRetrieveResponse(BaseModel):
    prompt: str
    matched_templates: list[dict[str, Any]]
    formatted_context: str


@router.get("/examples")
def get_rag_examples(domain: str | None = Query(None, description="Filter templates by domain")) -> list[dict[str, Any]]:
    """Retrieve available production dataset templates from the RAG knowledge base."""
    templates = rag_engine.templates
    if domain:
        domain_lower = domain.lower()
        templates = [t for t in templates if domain_lower in t.get("domain", "").lower()]
    return templates


@router.post("/retrieve", response_model=RAGRetrieveResponse)
def retrieve_rag_context(request: RAGRetrieveRequest) -> RAGRetrieveResponse:
    """Retrieve and format vector RAG context for a user prompt."""
    matches = rag_engine.retrieve(request.prompt, top_k=request.top_k)
    formatted = rag_engine.format_rag_context(request.prompt, top_k=request.top_k)
    return RAGRetrieveResponse(
        prompt=request.prompt,
        matched_templates=matches,
        formatted_context=formatted,
    )


@router.post("/reindex-vectors")
def reindex_vector_store() -> dict[str, Any]:
    """Force re-index and refresh vector embeddings for all knowledge base templates."""
    rag_engine.vector_store.index_templates(rag_engine.templates, force=True)
    return {
        "status": "success",
        "indexed_templates_count": len(rag_engine.templates),
        "cached_vectors_count": len(rag_engine.vector_store.vector_cache),
    }
