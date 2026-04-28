import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=4),
)
async def send_webhook(payload: dict[str, Any]) -> None:
    if not settings.webhook_url:
        logger.info("Webhook skipped because WEBHOOK_URL is not configured.")
        return

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            settings.webhook_url,
            json=payload,
        )

    response.raise_for_status()