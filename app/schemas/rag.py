from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    query: str = Field(min_length=3)
    top_k: int = Field(default=3, ge=1, le=10)


class RagDocumentChunk(BaseModel):
    source: str
    content: str
    score: float | None = None


class RagQueryResponse(BaseModel):
    query: str
    chunks: list[RagDocumentChunk]