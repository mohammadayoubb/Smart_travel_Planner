from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.agent import AgentQuestionRequest, AgentQuestionResponse
from app.services.agent_service import create_agent_run, update_agent_run
from app.services.rag_service import search_rag_documents

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


@router.post("/ask", response_model=AgentQuestionResponse)
async def ask_agent(
    request: AgentQuestionRequest,
    db: AsyncSession = Depends(get_db),
):
    run = await create_agent_run(
        db=db,
        user_id=request.user_id,
        question=request.question,
    )

    rag_results = search_rag_documents(
        query=request.question,
        top_k=3,
    )

    sources = ", ".join(result["source"] for result in rag_results)

    answer = (
        "Based on the current RAG search, the most relevant destination "
        f"documents are: {sources}. "
        "Later, the full agent will combine RAG, ML classification, and live APIs."
    )

    updated_run = await update_agent_run(
        db=db,
        run=run,
        answer=answer,
    )

    return AgentQuestionResponse(
        run_id=updated_run.id,
        answer=updated_run.answer,
        status=updated_run.status,
    )