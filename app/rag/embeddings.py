from openai import OpenAI

from app.config import get_settings

settings = get_settings()

client = OpenAI(api_key=settings.openai_api_key)


def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text,
    )

    return response.data[0].embedding


def embed_chunks(chunks: list[dict]) -> list[dict]:
    embedded = []

    for chunk in chunks:
        embedding = embed_text(chunk["content"])

        embedded.append(
            {
                **chunk,
                "embedding": embedding,
            }
        )

    return embedded