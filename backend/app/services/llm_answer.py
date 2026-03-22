from __future__ import annotations

import logging
import time

from openai import AsyncAzureOpenAI

from app.config import settings
from app.services.connection_manager import connection_manager, should_use_online_services

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are SaarthiAI, a careful assistant helping users understand Indian government schemes and welfare programs.

Rules:
- Ground answers in the provided LOCAL_SCHEMES_CONTEXT when it is non-empty.
- Use WEB_SEARCH_SNIPPETS only as supplementary hints; they may be incomplete or outdated.
- If information is uncertain, say what is known from the context and what is not verified.
- Respond in clear English (the caller may translate for the end user).
- Do not invent specific eligibility numbers, dates, or official portal URLs that are not in the context.
"""


async def generate_answer_with_azure(
    *,
    english_query: str,
    intent: str,
    local_context: str,
    web_context: str,
) -> str | None:
    # Check if we should use online services
    if settings.offline_only or not settings.azure_openai_configured():
        return None

    # Check connection manager for service health
    if not should_use_online_services() or not connection_manager.service_available("azure_openai"):
        logger.info("Azure OpenAI service unavailable, using offline mode")
        return None

    user_content = (
        f"Detected intent: {intent}\n"
        f"User question:\n{english_query}\n\n"
        f"LOCAL_SCHEMES_CONTEXT:\n{local_context or '(none)'}\n\n"
        f"WEB_SEARCH_SNIPPETS:\n{web_context or '(none)'}\n"
    )

    start_time = time.time()
    try:
        client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        completion = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.25,
            max_tokens=900,
        )

        response_time_ms = (time.time() - start_time) * 1000
        await connection_manager.record_success("azure_openai", response_time_ms)

        choice = completion.choices[0].message.content
        if not choice:
            return None
        return choice.strip()
    except Exception as exc:  # noqa: BLE001
        await connection_manager.record_failure("azure_openai", str(exc))
        logger.warning("Azure OpenAI completion failed; falling back to offline answer: %s", exc)
        return None
