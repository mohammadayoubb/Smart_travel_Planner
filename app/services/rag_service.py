from app.rag.chunker import chunk_documents
from app.rag.embeddings import embed_chunks, fake_embed
from app.rag.loader import load_documents
from app.rag.retriever import retrieve_top_k


def search_rag_documents(
    query: str,
    folder_path: str = "rag_documents",
    top_k: int = 3,
) -> list[dict]:
    documents = load_documents(folder_path)
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)

    query_embedding = fake_embed(query)

    results = retrieve_top_k(
        query_embedding=query_embedding,
        embedded_chunks=embedded_chunks,
        k=top_k,
    )

    return results