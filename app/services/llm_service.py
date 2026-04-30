from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()

client = AsyncOpenAI(api_key=settings.openai_api_key)


def calculate_openai_cost(
    input_tokens: int,
    output_tokens: int,
    input_cost_per_1m: float,
    output_cost_per_1m: float,
) -> float:
    input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
    output_cost = (output_tokens / 1_000_000) * output_cost_per_1m

    return round(input_cost + output_cost, 6)


async def cheap_model_rewrite_query(question: str) -> dict:
    response = await client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Rewrite the user's travel request into a short search query. "
                    "Focus on destination type, budget, weather, activities, and travel style. "
                    "Return plain text only."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    content = response.choices[0].message.content or question
    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0

    return {
        "model": settings.openai_chat_model,
        "rewritten_query": content.strip(),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": calculate_openai_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_per_1m=0.15,
            output_cost_per_1m=0.60,
        ),
    }


async def strong_model_final_answer(
    question: str,
    destination: str,
    predicted_style: str,
    destination_context: str,
    weather: dict,
) -> dict:
    response = await client.chat.completions.create(
        model=settings.openai_final_model,
        messages=[
            {
                "role": "system",
                "content": (
                     "You are a helpful travel planning assistant. "
                    "Write in a natural conversational style, not like a rigid checklist. "
                    "Always include the travel style near the beginning using this exact line: "
                    "'Travel Style: <predicted_style>'. "
                    "Always include current weather if it is available. "
                    "If weather is unavailable, briefly say that live weather could not be retrieved. "
                    "Do not use markdown bold stars like ** anywhere. "
                    "Do not mention internal tools, RAG, embeddings, vector databases, or ML. "
                    "If live weather conflicts with the user's request, explain that clearly."
                                ),
            },
            {
                "role": "user",
                "content": f"""
User question:
{question}

Suggested destination:
{destination}

Predicted travel style:
{predicted_style}

Destination context:
{destination_context}

Current weather:
weather_text = (
    f"{weather.get('temperature_c')}°C, "
    f"{weather.get('weather')}, "
    f"Humidity: {weather.get('humidity')}%"
    if weather.get("temperature_c") is not None
    else "Weather data unavailable"
)
""",
            },
        ],
    )

    content = response.choices[0].message.content or ""
    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0

    return {
        "model": settings.openai_final_model,
        "answer": content.strip(),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": calculate_openai_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_per_1m=2.50,
            output_cost_per_1m=10.00,
        ),
    }