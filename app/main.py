from fastapi import FastAPI

from app.config import get_settings
from app.routes.auth import router as auth_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
    }