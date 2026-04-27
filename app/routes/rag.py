from fastapi import APIRouter

from app.schemas.rag import RagDocumentChunk, RagQueryRequest, RagQueryResponse
from app.services.rag_service import search_rag_documents

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.post("/search", response_model=RagQueryResponse)
async def search_rag(
    request: RagQueryRequest,
):
    results = search_rag_documents(
        query=request.query,
        top_k=request.top_k,
    )

    chunks = [
        RagDocumentChunk(
            source=result["source"],
            content=result["content"],
            score=result["score"],
        )
        for result in results
    ]

    return RagQueryResponse(
        query=request.query,
        chunks=chunks,
    )