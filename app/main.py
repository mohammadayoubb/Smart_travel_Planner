from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.environment
    }