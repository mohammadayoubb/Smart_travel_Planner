import httpx


async def get_weather_summary(city: str) -> dict:
    url = "https://wttr.in/{city}".format(city=city)

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            url,
            params={"format": "j1"},
        )

    response.raise_for_status()
    data = response.json()

    current = data["current_condition"][0]

    return {
        "city": city,
        "temperature_c": current.get("temp_C"),
        "weather": current["weatherDesc"][0]["value"],
        "humidity": current.get("humidity"),
    }