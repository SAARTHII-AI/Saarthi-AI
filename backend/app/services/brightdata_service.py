import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)


def search_schemes(query: str, top_k: int = 3) -> list[str]:
    """
    Search Bright Data SERP API for relevant government scheme snippets.
    Returns a list of organic result snippet strings.
    Falls back to empty list silently on any failure or missing credentials.
    """
    token = settings.brightdata_api_token
    zone = settings.brightdata_serp_zone

    if not token or not zone:
        return []

    try:
        search_query = f"{query} government scheme india site:gov.in OR site:india.gov.in"
        url = "https://api.brightdata.com/datasets/v3/trigger"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "zone": zone,
            "url": f"https://www.google.com/search?q={requests.utils.quote(search_query)}&num=5",
            "format": "json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=8)
        resp.raise_for_status()

        data = resp.json()

        snippets = []
        organic = data.get("organic", []) if isinstance(data, dict) else []
        for item in organic[:top_k]:
            snippet = item.get("description") or item.get("snippet") or item.get("title", "")
            if snippet:
                snippets.append(snippet.strip())

        return snippets

    except Exception as e:
        logger.warning(f"Bright Data SERP search failed (non-fatal): {e}")
        return []
