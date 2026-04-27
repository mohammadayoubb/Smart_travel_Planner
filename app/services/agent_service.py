from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_run import AgentRun


async def create_agent_run(
    db: AsyncSession,
    user_id: int,
    question: str,
) -> AgentRun:
    run = AgentRun(
        user_id=user_id,
        question=question,
        status="pending",
    )

    db.add(run)
    await db.commit()
    await db.refresh(run)

    return run


async def update_agent_run(
    db: AsyncSession,
    run: AgentRun,
    answer: str,
) -> AgentRun:
    run.answer = answer
    run.status = "completed"

    await db.commit()
    await db.refresh(run)

    return run