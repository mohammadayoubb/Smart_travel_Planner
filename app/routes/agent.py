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


def extract_destination_name(source: str) -> str:
    return source.replace(".txt", "").replace("_", " ").title()


def detect_travel_intents(question: str) -> list[str]:
    q = question.lower()
    intents = []

    if any(word in q for word in ["cheap", "budget", "affordable", "low cost", "not expensive"]):
        intents.append("budget-friendly travel")

    if any(word in q for word in ["food", "eat", "restaurant", "cuisine", "local dishes"]):
        intents.append("local food experiences")

    if any(word in q for word in ["culture", "history", "historical", "museum", "temple", "heritage"]):
        intents.append("culture and historical attractions")

    if any(word in q for word in ["family", "kids", "children", "safe", "safety"]):
        intents.append("family-friendly and safe travel")

    if any(word in q for word in ["adventure", "hiking", "mountain", "outdoor", "trekking", "nature"]):
        intents.append("outdoor and adventure activities")

    if any(word in q for word in ["relax", "relaxation", "beach", "resort", "calm", "quiet"]):
        intents.append("relaxation and calm experiences")

    if any(word in q for word in ["luxury", "premium", "hotel", "resort", "fine dining"]):
        intents.append("luxury travel")

    if any(word in q for word in ["warm", "sunny", "hot", "summer"]):
        intents.append("warm weather")

    return intents


def build_weather_note(question: str, weather: dict) -> str:
    q = question.lower()

    if not any(word in q for word in ["weather", "warm", "sunny", "hot", "cold", "snow"]):
        return ""

    temp = weather.get("temperature_c")

    try:
        temp_num = float(temp)
    except (TypeError, ValueError):
        return "Current weather could not be verified clearly, so check conditions again before booking."

    if any(word in q for word in ["snow", "ski", "cold"]):
        if temp_num <= 5:
            return "The current weather also fits your preference for a colder or winter-style destination."
        return (
            f"The destination may fit the activity style, but the current temperature is {temp_num:g}°C, "
            "so it may not currently feel like a cold or snowy destination."
        )

    if any(word in q for word in ["warm", "sunny", "hot"]):
        if temp_num >= 20:
            return "The current weather also supports your preference for warm conditions."
        return (
            f"The destination matches some of your preferences, but the current temperature is {temp_num:g}°C, "
            "so it may not match your warm-weather preference right now."
        )

    return ""


def build_reason_text(intents: list[str]) -> str:
    if not intents:
        return "This destination was selected because it best matches the overall meaning of your question."

    if len(intents) == 1:
        return f"This destination was selected because it matches your interest in {intents[0]}."

    return (
        "This destination was selected because it matches your interest in "
        + ", ".join(intents[:-1])
        + f", and {intents[-1]}."
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
        answer = "I could not find a suitable destination from the available travel knowledge base."

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

    top_result = rag_results[0]
    destination = extract_destination_name(top_result["source"])
    destination_context = top_result["content"]

    intents = detect_travel_intents(request.question)
    reason_text = build_reason_text(intents)

    try:
        weather = await get_weather_summary(destination)
    except Exception:
        weather = {
            "temperature_c": "N/A",
            "weather": "weather unavailable",
        }

    weather_note = build_weather_note(request.question, weather)

    answer = (
        f"Suggested Destination: {destination}\n\n"
        f"Why this fits your request:\n"
        f"{reason_text}\n\n"
        f"Destination Details:\n"
        f"{destination_context}\n\n"
        f"Current Weather:\n"
        f"{weather['temperature_c']}°C with {weather['weather']}\n"
    )

    if weather_note:
        answer += f"{weather_note}\n\n"
    else:
        answer += "\n"

    answer += (
        f"Recommendation:\n"
        f"Compare this destination with the other suggested options before booking, especially if weather, budget, or crowd level is important to you."
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