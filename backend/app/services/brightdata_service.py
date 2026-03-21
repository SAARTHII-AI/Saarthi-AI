import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)


def search_schemes(query: str, top_k: int = 3) -> list[str]:
    """
    Search Bright Data SERP API for relevant government scheme snippets.
    Returns a list of organic result snippet strings.
    Falls back to empty list silently on any failure, missing credentials,
    or when OFFLINE_ONLY is enabled.
    """
    if settings.offline_only:
        return []

    token = settings.brightdata_api_token
    zone = settings.brightdata_serp_zone

    if not token or not zone:
        return []

    try:
        search_query = f"{query} government scheme india"

        # Bright Data SERP zone — proxy-style synchronous request.
        # The zone is configured as a SERP API zone; we make a standard
        # Google search request through the Bright Data proxy endpoint.
        url = "https://api.brightdata.com/request"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "zone": zone,
            "url": f"https://www.google.com/search?q={requests.utils.quote(search_query)}&num=5",
            "format": "json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=12)
        resp.raise_for_status()

        data = resp.json()

        snippets = []

        # Bright Data SERP zone returns structured JSON with organic results
        organic = []
        if isinstance(data, dict):
            organic = (
                data.get("organic")
                or data.get("results", {}).get("organic", [])
                or []
            )
        elif isinstance(data, list):
            organic = data

        for item in organic[:top_k]:
            snippet = (
                item.get("description")
                or item.get("snippet")
                or item.get("title", "")
            )
            if snippet:
                snippets.append(snippet.strip())

        return snippets

    except Exception as e:
        logger.warning(f"Bright Data SERP search failed (non-fatal): {e}")
        return []
