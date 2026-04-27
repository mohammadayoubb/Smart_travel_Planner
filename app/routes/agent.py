from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.agent import AgentQuestionRequest, AgentQuestionResponse
from app.services.agent_service import create_agent_run, update_agent_run
from app.services.rag_store_service import search_stored_rag_chunks
from app.services.weather_service import get_weather_summary

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

    rag_results = await search_stored_rag_chunks(
        db=db,
        query=request.question,
        top_k=3,
    )

    weather = await get_weather_summary("Madeira")

    sources = ", ".join(result["source"] for result in rag_results)

    answer = (
        "Based on the RAG search, the most relevant destination documents are: "
        f"{sources}. "
        f"The live weather check for Madeira shows {weather['temperature_c']}°C "
        f"and {weather['weather']}. "
        "The full agent will later use stronger LLM synthesis, ML classification, "
        "and better destination extraction."
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