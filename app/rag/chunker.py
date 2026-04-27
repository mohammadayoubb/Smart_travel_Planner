def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict]:
    chunks = []

    for document in documents:
        text_chunks = chunk_text(
            document["content"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for index, chunk in enumerate(text_chunks):
            chunks.append(
                {
                    "source": document["source"],
                    "chunk_index": index,
                    "content": chunk,
                }
            )

    return chunks