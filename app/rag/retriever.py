import math


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    min_len = min(len(vec1), len(vec2))

    dot = sum(vec1[i] * vec2[i] for i in range(min_len))
    norm1 = math.sqrt(sum(v * v for v in vec1[:min_len]))
    norm2 = math.sqrt(sum(v * v for v in vec2[:min_len]))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot / (norm1 * norm2)


def retrieve_top_k(
    query_embedding: list[float],
    embedded_chunks: list[dict],
    k: int = 3,
) -> list[dict]:
    scored = []

    for chunk in embedded_chunks:
        score = cosine_similarity(query_embedding, chunk["embedding"])

        scored.append(
            {
                **chunk,
                "score": score,
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:k]