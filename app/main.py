from fastapi import FastAPI

from app.config import get_settings
from app.routes.agent import router as agent_router
from app.routes.auth import router as auth_router
from app.routes.rag import router as rag_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(rag_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
    }