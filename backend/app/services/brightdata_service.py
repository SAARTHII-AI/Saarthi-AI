import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)

GOV_SITES = ["data.gov.in", "india.gov.in", "pmkisan.gov.in", "agricoop.nic.in", "pib.gov.in"]


def _is_safe_url(url: str) -> bool:
    if not url:
        return False
    url_lower = url.lower().strip()
    return url_lower.startswith("http://") or url_lower.startswith("https://")


def search_schemes(query: str, top_k: int = 3) -> list[str]:
    if settings.offline_only:
        return []

    token = settings.brightdata_api_token
    zone = settings.brightdata_serp_zone

    if not token or not zone:
        return []

    try:
        search_query = f"{query} government scheme india site:india.gov.in OR site:data.gov.in OR site:pib.gov.in"

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

        organic = []
        if isinstance(data, dict):
            organic = (
                data.get("organic")
                or data.get("results", {}).get("organic", [])
                or []
            )
        elif isinstance(data, list):
            organic = data

        for item in organic[:top_k * 2]:
            title = item.get("title", "")
            snippet = (
                item.get("description")
                or item.get("snippet")
                or title
            )
            link = item.get("link") or item.get("url", "")
            if not snippet:
                continue

            is_gov = False
            source_tag = ""
            if link:
                for gov_site in GOV_SITES:
                    if gov_site in link:
                        is_gov = True
                        source_tag = f" [Source: {gov_site}]"
                        break

            if is_gov:
                snippets.insert(0, f"{snippet.strip()}{source_tag}")
            elif len(snippets) < top_k:
                snippets.append(snippet.strip())

        return snippets[:top_k]

    except Exception as e:
        logger.warning(f"Bright Data SERP search failed (non-fatal): {e}")
        return []


def search_document_links(query: str, scheme_name: str) -> list[dict]:
    if settings.offline_only:
        return []

    token = settings.brightdata_api_token
    zone = settings.brightdata_serp_zone

    if not token or not zone:
        return []

    try:
        search_query = f"{scheme_name} apply online documents official site india.gov.in OR data.gov.in"

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

        organic = []
        if isinstance(data, dict):
            organic = (
                data.get("organic")
                or data.get("results", {}).get("organic", [])
                or []
            )
        elif isinstance(data, list):
            organic = data

        results = []
        for item in organic[:8]:
            title = item.get("title", "")
            link = item.get("link") or item.get("url", "")
            snippet = item.get("description") or item.get("snippet", "")
            if not title or not link:
                continue
            if not _is_safe_url(link):
                continue
            results.append({"title": title.strip(), "url": link.strip(), "snippet": snippet.strip()})

        return results[:5]

    except Exception as e:
        logger.warning(f"Bright Data document link search failed (non-fatal): {e}")
        return []
