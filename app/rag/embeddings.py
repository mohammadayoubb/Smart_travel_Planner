from typing import List


def fake_embed(text: str) -> List[float]:
    """
    Temporary embedding function.
    Converts text into a simple numeric vector.
    We will replace this later with real OpenAI embeddings.
    """
    return [float(ord(char)) for char in text[:100]]


def embed_chunks(chunks: list[dict]) -> list[dict]:
    embedded = []

    for chunk in chunks:
        embedding = fake_embed(chunk["content"])

        embedded.append(
            {
                **chunk,
                "embedding": embedding,
            }
        )

    return embedded