from fastapi import APIRouter, Depends
from langsmith import traceable
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.agent import AgentQuestionRequest, AgentQuestionResponse
from app.schemas.ml import TravelStyleFeatures
from app.services.agent_service import create_agent_run, update_agent_run
from app.services.llm_service import cheap_model_rewrite_query, strong_model_final_answer
from app.services.ml_service import predict_travel_style
from app.services.rag_store_service import search_stored_rag_chunks
from app.services.tool_log_service import log_tool_call
from app.services.weather_service import get_weather_summary
from app.services.webhook_service import send_webhook

router = APIRouter(prefix="/agent", tags=["Agent"])


def extract_destination_name(source: str) -> str:
    return source.replace(".txt", "").replace("_", " ").title()


def build_ml_features(destination: str, context: str, question: str) -> TravelStyleFeatures:
    text = f"{destination} {context} {question}".lower()

    return TravelStyleFeatures(
        avg_daily_budget_usd=60 if any(w in text for w in ["cheap", "budget", "affordable", "hanoi"]) else 140,
        warm_weather_score=9 if any(w in text for w in ["warm", "beach", "bali", "phuket", "hanoi"]) else 5,
        tourist_crowd_score=4 if any(w in text for w in ["quiet", "fewer crowds", "not touristy"]) else 7,
        hiking_score=9 if any(w in text for w in ["hiking", "mountain", "trekking", "patagonia", "queenstown", "madeira"]) else 4,
        beach_score=9 if any(w in text for w in ["beach", "island", "bali", "phuket", "madeira"]) else 2,
        museum_score=9 if any(w in text for w in ["culture", "history", "museum", "temple", "rome", "kyoto", "cairo"]) else 4,
        nightlife_score=7 if any(w in text for w in ["nightlife", "restaurant", "food"]) else 4,
        family_score=8 if any(w in text for w in ["family", "kids", "safe"]) else 5,
        luxury_score=8 if any(w in text for w in ["luxury", "premium", "resort", "dubai"]) else 4,
        safety_score=8 if any(w in text for w in ["safe", "family", "japan", "kyoto"]) else 6,
        description=context,
    )


async def safe_send_webhook(run_id: int, user_id: int, question: str, answer: str, status: str) -> None:
    try:
        await send_webhook(
            {
                "run_id": run_id,
                "user_id": user_id,
                "question": question,
                "answer": answer,
                "status": status,
            }
        )
    except Exception:
        pass


@traceable(name="cheap_model_rewrite")
async def traced_rewrite_query(question: str) -> dict:
    return await cheap_model_rewrite_query(question)


@traceable(name="rag_retrieval")
async def traced_rag_search(db: AsyncSession, query: str, top_k: int) -> list[dict]:
    return await search_stored_rag_chunks(db=db, query=query, top_k=top_k)


@traceable(name="ml_classification")
def traced_ml_prediction(features: TravelStyleFeatures) -> str:
    return predict_travel_style(features)


@traceable(name="weather_fetch")
async def traced_weather_fetch(destination: str) -> dict:
    return await get_weather_summary(destination)


@traceable(name="final_llm_synthesis")
async def traced_final_answer(
    question: str,
    destination: str,
    predicted_style: str,
    destination_context: str,
    weather: dict,
) -> dict:
    return await strong_model_final_answer(
        question=question,
        destination=destination,
        predicted_style=predicted_style,
        destination_context=destination_context,
        weather=weather,
    )


@router.post("/ask", response_model=AgentQuestionResponse)
@traceable(name="travel_agent_run")
async def ask_agent(
    request: AgentQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    run = await create_agent_run(
        db=db,
        user_id=current_user.id,
        question=request.question,
    )

    rewrite_result = await traced_rewrite_query(request.question)

    await log_tool_call(
        db=db,
        agent_run_id=run.id,
        tool_name="cheap_llm_query_rewrite",
        tool_input={"question": request.question},
        tool_output=rewrite_result,
    )

    rag_results = await traced_rag_search(
        db=db,
        query=rewrite_result["rewritten_query"],
        top_k=3,
    )

    await log_tool_call(
        db=db,
        agent_run_id=run.id,
        tool_name="rag_retrieval",
        tool_input={
            "original_query": request.question,
            "rewritten_query": rewrite_result["rewritten_query"],
            "top_k": 3,
        },
        tool_output={
            "sources": [result["source"] for result in rag_results],
        },
    )

    if not rag_results:
        answer = "I could not find a suitable destination from the available travel knowledge base."

        updated_run = await update_agent_run(db=db, run=run, answer=answer)

        await safe_send_webhook(
            run_id=updated_run.id,
            user_id=current_user.id,
            question=request.question,
            answer=updated_run.answer,
            status=updated_run.status,
        )

        return AgentQuestionResponse(
            run_id=updated_run.id,
            answer=updated_run.answer,
            status=updated_run.status,
        )

    top_result = rag_results[0]
    destination = extract_destination_name(top_result["source"])
    destination_context = top_result["content"]

    ml_features = build_ml_features(
        destination=destination,
        context=destination_context,
        question=request.question,
    )

    predicted_style = traced_ml_prediction(ml_features)

    await log_tool_call(
        db=db,
        agent_run_id=run.id,
        tool_name="ml_classifier",
        tool_input=ml_features.model_dump(),
        tool_output={"predicted_style": predicted_style},
    )

    try:
        weather = await traced_weather_fetch(destination)
        weather_status = "success"
    except Exception as exc:
        weather = {
            "temperature_c": "N/A",
            "weather": "weather unavailable",
            "error": str(exc),
        }
        weather_status = "error"

    await log_tool_call(
        db=db,
        agent_run_id=run.id,
        tool_name="weather_api",
        tool_input={"destination": destination},
        tool_output=weather,
        status=weather_status,
    )

    final_result = await traced_final_answer(
        question=request.question,
        destination=destination,
        predicted_style=predicted_style,
        destination_context=destination_context,
        weather=weather,
    )

    await log_tool_call(
        db=db,
        agent_run_id=run.id,
        tool_name="strong_llm_final_synthesis",
        tool_input={
            "question": request.question,
            "destination": destination,
            "predicted_style": predicted_style,
        },
        tool_output=final_result,
    )

    answer = final_result["answer"]

    updated_run = await update_agent_run(db=db, run=run, answer=answer)

    await safe_send_webhook(
        run_id=updated_run.id,
        user_id=current_user.id,
        question=request.question,
        answer=updated_run.answer,
        status=updated_run.status,
    )

    return AgentQuestionResponse(
        run_id=updated_run.id,
        answer=updated_run.answer,
        status=updated_run.status,
    )