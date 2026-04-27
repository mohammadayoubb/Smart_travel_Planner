import asyncio

from app.database import Base, engine
from app.models.agent_run import AgentRun
from app.models.rag_chunk import RagChunk
from app.models.tool_call_log import ToolCallLog
from app.models.user import User


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully.")


if __name__ == "__main__":
    asyncio.run(create_tables())