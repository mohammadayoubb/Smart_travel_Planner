from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rag_chunk import RagChunk
from app.rag.chunker import chunk_documents
from app.rag.embeddings import embed_chunks, embed_text
from app.rag.loader import load_documents
from app.rag.retriever import cosine_similarity


async def ingest_rag_documents(
    db: AsyncSession,
    folder_path: str = "rag_documents",
) -> int:
    await db.execute(delete(RagChunk))

    documents = load_documents(folder_path)
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)

    for chunk in embedded_chunks:
        db.add(
            RagChunk(
                source=chunk["source"],
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                embedding=chunk["embedding"],
            )
        )

    await db.commit()
    return len(embedded_chunks)


async def search_stored_rag_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 3,
) -> list[dict]:
    query_embedding = embed_text(query)

    result = await db.execute(select(RagChunk))
    chunks = result.scalars().all()

    scored = []

    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk.embedding)

        scored.append(
            {
                "source": chunk.source,
                "content": chunk.content,
                "score": score,
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]