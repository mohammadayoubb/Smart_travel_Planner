import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tool_call_log import ToolCallLog


async def log_tool_call(
    db: AsyncSession,
    agent_run_id: int,
    tool_name: str,
    tool_input: dict[str, Any],
    tool_output: dict[str, Any],
    status: str = "success",
) -> ToolCallLog:
    tool_log = ToolCallLog(
        agent_run_id=agent_run_id,
        tool_name=tool_name,
        tool_input=json.dumps(tool_input),
        tool_output=json.dumps(tool_output),
        status=status,
    )

    db.add(tool_log)
    await db.commit()
    await db.refresh(tool_log)

    return tool_log