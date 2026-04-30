from pydantic import BaseModel, Field
from typing import Optional

class AgentQuestionResponse(BaseModel):
    run_id: int
    answer: str
    status: str
    total_cost_usd: Optional[float] = None
    
class AgentQuestionRequest(BaseModel):
    question: str = Field(min_length=5)


class AgentQuestionResponse(BaseModel):
    run_id: int
    answer: str
    status: str