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

    if not rag_results:
        answer = "I could not find relevant destination documents. Please run /rag/ingest first."

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

    destination = rag_results[0]["source"].replace(".txt", "").replace("_", " ").title()
    sources = ", ".join(result["source"] for result in rag_results)

    try:
        weather = await get_weather_summary(destination)
    except Exception:
        weather = {
            "temperature_c": "N/A",
            "weather": "weather unavailable",
        }

    answer = f"""
     Suggested Destination: {destination}

    , Why this fits your request:
    This destination matches your preference for warm weather, outdoor activities like hiking, and fewer crowds compared to highly touristy locations.

    Current Weather:
    {weather['temperature_c']}°C with {weather['weather']}

    , How this was chosen:
    - RAG retrieved: {sources}
    - Live weather data was checked
    - Future step: ML model will classify travel style

    , Recommendation:
    Consider planning your trip during shoulder season for the best balance between weather and crowd levels.
    """

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