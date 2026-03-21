from __future__ import annotations

import logging
import time
from typing import List
from urllib.parse import quote_plus

import httpx

from app.config import settings
from app.schemas import DocumentLink
from app.services.connection_manager import connection_manager, should_use_online_services

logger = logging.getLogger(__name__)


def _build_google_search_url(query: str, hl: str = "en", gl: str = "in") -> str:
    q = quote_plus(query)
    return f"https://www.google.com/search?q={q}&hl={hl}&gl={gl}"


async def fetch_serp_snippets(english_query: str) -> str:
    """
    Returns a short text block of organic SERP snippets via Bright Data REST `/request`, or "" on skip/failure.

    `brightdata-sdk` is listed in requirements for CLI/SDK workflows; this path uses httpx so the API can
    target an explicit `BRIGHTDATA_SERP_ZONE` without SDK zone bootstrap (better fit for Lambda/Vercel).
    """
    if settings.offline_only or not settings.brightdata_serp_configured():
        return ""

    # Check connection manager for service health
    if not should_use_online_services() or not connection_manager.service_available("brightdata_serp"):
        logger.info("BrightData SERP service unavailable, skipping web context")
        return ""

    search_query = f"{english_query} India government scheme welfare subsidy"
    payload = {
        "zone": settings.brightdata_serp_zone,
        "url": _build_google_search_url(search_query),
        "format": "raw",
        "data_format": "parsed_light",
    }
    headers = {
        "Authorization": f"Bearer {settings.brightdata_api_token}",
        "Content-Type": "application/json",
    }

    start_time = time.time()
    try:
        timeout = httpx.Timeout(settings.brightdata_serp_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                settings.brightdata_request_url,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        response_time_ms = (time.time() - start_time) * 1000
        await connection_manager.record_success("brightdata_serp", response_time_ms)

    except Exception as exc:  # noqa: BLE001 — network/provider errors should not break the API
        await connection_manager.record_failure("brightdata_serp", str(exc))
        logger.warning("Bright Data SERP request failed; continuing without web context: %s", exc)
        return ""

    organic = data.get("organic") or []
    lines: list[str] = []
    for item in organic[:8]:
        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()
        link = (item.get("link") or "").strip()
        if title or description:
            lines.append(f"- {title}: {description} ({link})".strip())

    return "\n".join(lines).strip()


# Simple in-memory cache for document links (scheme_name + doc_type -> results)
# In production, consider using Redis or similar for distributed caching
_document_links_cache: dict[str, tuple[float, List[DocumentLink]]] = {}
_CACHE_TTL_SECONDS = 3600  # 1 hour cache TTL


def _extract_source_domain(url: str) -> str:
    """Extract the domain name from a URL for source attribution."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove common prefixes
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return "web"


def _is_official_source(url: str) -> bool:
    """Check if URL is from an official government or trusted source."""
    official_domains = [
        ".gov.in", ".nic.in", ".india.gov.in",
        "pmkisan.gov.in", "pmjay.gov.in", "pib.gov.in",
        "mygov.in", "meity.gov.in", "rural.nic.in",
        "nrega.nic.in", "nsap.nic.in", "uidai.gov.in",
    ]
    url_lower = url.lower()
    return any(domain in url_lower for domain in official_domains)


def _build_document_search_query(scheme_name: str, document_type: str) -> str:
    """Build an optimized search query for document links."""
    # Clean the scheme name and document type
    scheme_clean = scheme_name.strip()
    doc_type_clean = document_type.strip() if document_type else "documents"

    # Build a targeted search query
    return f"{scheme_clean} {doc_type_clean} official link site:gov.in OR site:nic.in"


def _get_cache_key(scheme_name: str, document_type: str) -> str:
    """Generate a cache key for document links."""
    return f"{scheme_name.lower().strip()}:{document_type.lower().strip()}"


async def fetch_document_links(
    scheme_name: str,
    document_type: str = "documents",
) -> List[DocumentLink]:
    """
    Fetch official document links for a government scheme using BrightData SERP API.

    Args:
        scheme_name: Name of the government scheme (e.g., "PM-KISAN", "Ayushman Bharat")
        document_type: Type of document to search for (e.g., "Aadhaar", "application form", "eligibility")

    Returns:
        List of DocumentLink objects with title, url, description, and source.
        Returns empty list on failure or when offline.
    """
    # Check if we're offline or not configured
    if settings.offline_only or not settings.brightdata_serp_configured():
        logger.debug("Document links search skipped: offline mode or BrightData not configured")
        return []

    # Check connection manager for service health
    if not should_use_online_services() or not connection_manager.service_available("brightdata_serp"):
        logger.info("BrightData SERP service unavailable, skipping document links search")
        return []

    # Validate inputs
    if not scheme_name or not scheme_name.strip():
        logger.debug("Document links search skipped: empty scheme name")
        return []

    # Check cache first
    cache_key = _get_cache_key(scheme_name, document_type)
    current_time = time.time()

    if cache_key in _document_links_cache:
        cached_time, cached_results = _document_links_cache[cache_key]
        if current_time - cached_time < _CACHE_TTL_SECONDS:
            logger.debug("Document links cache hit for: %s", cache_key)
            return cached_results
        else:
            # Cache expired, remove it
            del _document_links_cache[cache_key]

    # Build the search query
    search_query = _build_document_search_query(scheme_name, document_type)

    payload = {
        "zone": settings.brightdata_serp_zone,
        "url": _build_google_search_url(search_query),
        "format": "raw",
        "data_format": "parsed_light",
    }
    headers = {
        "Authorization": f"Bearer {settings.brightdata_api_token}",
        "Content-Type": "application/json",
    }

    start_time = time.time()
    try:
        timeout = httpx.Timeout(settings.brightdata_serp_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                settings.brightdata_request_url,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        response_time_ms = (time.time() - start_time) * 1000
        await connection_manager.record_success("brightdata_serp", response_time_ms)

    except Exception as exc:
        await connection_manager.record_failure("brightdata_serp", str(exc))
        logger.warning(
            "BrightData document links request failed for '%s'; returning empty list: %s",
            scheme_name,
            exc,
        )
        return []

    # Parse organic results into DocumentLink objects
    organic = data.get("organic") or []
    document_links: List[DocumentLink] = []

    # Prioritize official sources
    official_results = []
    other_results = []

    for item in organic[:15]:  # Check more results to find official sources
        url = (item.get("link") or "").strip()
        if not url:
            continue

        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()

        if not title:
            continue

        source = _extract_source_domain(url)
        doc_link = DocumentLink(
            title=title,
            url=url,
            description=description or f"Official information about {scheme_name}",
            source=source,
        )

        if _is_official_source(url):
            official_results.append(doc_link)
        else:
            other_results.append(doc_link)

    # Combine results: official sources first, then others, limited to 5 total
    document_links = (official_results + other_results)[:5]

    # Cache the results
    _document_links_cache[cache_key] = (current_time, document_links)

    # Limit cache size to prevent memory issues (simple LRU-like cleanup)
    if len(_document_links_cache) > 100:
        # Remove oldest entries
        sorted_keys = sorted(
            _document_links_cache.keys(),
            key=lambda k: _document_links_cache[k][0],
        )
        for old_key in sorted_keys[:20]:
            del _document_links_cache[old_key]

    logger.info(
        "Fetched %d document links for scheme '%s' (doc_type: %s)",
        len(document_links),
        scheme_name,
        document_type,
    )

    return document_links


def clear_document_links_cache() -> None:
    """Clear the document links cache. Useful for testing or manual cache invalidation."""
    _document_links_cache.clear()
    logger.info("Document links cache cleared")
