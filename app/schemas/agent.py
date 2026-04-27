from pydantic import BaseModel, Field


class AgentQuestionRequest(BaseModel):
    user_id: int = Field(gt=0)
    question: str = Field(min_length=5)


class AgentQuestionResponse(BaseModel):
    run_id: int
    answer: str
    status: str