from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.rag import RagDocumentChunk, RagQueryRequest, RagQueryResponse
from app.services.rag_store_service import ingest_rag_documents, search_stored_rag_chunks

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.post("/ingest")
async def ingest_rag(
    db: AsyncSession = Depends(get_db),
):
    chunk_count = await ingest_rag_documents(db)

    return {
        "status": "success",
        "chunks_ingested": chunk_count,
    }


@router.post("/search", response_model=RagQueryResponse)
async def search_rag(
    request: RagQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    results = await search_stored_rag_chunks(
        db=db,
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