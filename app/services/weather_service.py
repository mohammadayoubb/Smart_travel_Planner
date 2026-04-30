import httpx


WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    51: "Light drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    80: "Rain showers",
    95: "Thunderstorm",
}


async def get_coordinates(city: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )

    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])

    if not results:
        raise ValueError(f"No coordinates found for {city}")

    location = results[0]

    return {
        "city": location.get("name", city),
        "country": location.get("country", ""),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
    }


async def get_weather_summary(city: str) -> dict:
    location = await get_coordinates(city)

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,weather_code",
                "timezone": "auto",
            },
        )

    response.raise_for_status()
    data = response.json()
    current = data.get("current", {})

    temperature = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    weather_code = current.get("weather_code")

    return {
        "city": location["city"],
        "country": location["country"],
        "temperature_c": temperature,
        "weather": WEATHER_CODE_MAP.get(weather_code, "Weather condition unavailable"),
        "humidity": humidity,
    }