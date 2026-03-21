import logging
import time
from typing import Optional
import requests
from app.config import settings

logger = logging.getLogger(__name__)

GOV_DATA_ENDPOINTS = {
    "msp": {
        "url": "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
        "description": "Minimum Support Prices for major crops",
    },
    "agriculture_stats": {
        "url": "https://api.data.gov.in/resource/35be3986-0576-4b57-a583-4f98f5d68484",
        "description": "Agriculture production statistics",
    },
    "soil_health": {
        "url": "https://api.data.gov.in/resource/4a4d1e8a-6c8a-4f5e-9e2e-0cd69e88b1e5",
        "description": "Soil health card data",
    },
}

RELIABLE_GOV_SOURCES = [
    {
        "name": "PM-KISAN Portal",
        "url": "https://pmkisan.gov.in/",
        "topics": ["pm-kisan", "kisan samman", "farmer income support"],
    },
    {
        "name": "PMFBY Crop Insurance",
        "url": "https://pmfby.gov.in/",
        "topics": ["crop insurance", "pmfby", "fasal bima"],
    },
    {
        "name": "eNAM Mandi Portal",
        "url": "https://enam.gov.in/web/",
        "topics": ["mandi", "market price", "crop price", "msp"],
    },
    {
        "name": "Soil Health Card Portal",
        "url": "https://soilhealth.dac.gov.in/",
        "topics": ["soil health", "soil testing", "soil card"],
    },
    {
        "name": "Agriculture Ministry",
        "url": "https://agricoop.nic.in/",
        "topics": ["agriculture", "farming", "crop", "scheme"],
    },
    {
        "name": "India.gov.in Schemes",
        "url": "https://www.india.gov.in/my-government/schemes",
        "topics": ["government scheme", "sarkari yojana"],
    },
    {
        "name": "Kisan Call Center (1800-180-1551)",
        "url": "https://dackkms.gov.in/",
        "topics": ["help", "assistance", "call center", "kisan"],
    },
    {
        "name": "DBT Agriculture Portal",
        "url": "https://dbtagriculture.bihar.gov.in/",
        "topics": ["dbt", "direct benefit", "subsidy", "bihar"],
    },
]

_cache = {}
_CACHE_TTL = 3600


def _get_cached(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["data"]
    return None


def _set_cache(key: str, data):
    if len(_cache) > 100:
        oldest = min(_cache, key=lambda k: _cache[k]["ts"])
        del _cache[oldest]
    _cache[key] = {"data": data, "ts": time.time()}


def fetch_msp_data(crop: Optional[str] = None) -> list[dict]:
    cache_key = f"msp_{crop or 'all'}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    api_key = getattr(settings, "data_gov_api_key", None)

    try:
        if not api_key:
            logger.info("data.gov.in API key not configured, skipping MSP fetch")
            return []

        params = {
            "api-key": api_key,
            "format": "json",
            "limit": 20,
        }
        if crop:
            params["filters[commodity]"] = crop.title()

        endpoint = GOV_DATA_ENDPOINTS["msp"]["url"]
        resp = requests.get(endpoint, params=params, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            records = data.get("records", [])
            result = []
            for rec in records[:10]:
                result.append({
                    "commodity": rec.get("commodity", ""),
                    "variety": rec.get("variety", ""),
                    "msp": rec.get("msp_rs_per_quintal_", ""),
                    "year": rec.get("year", ""),
                })
            _set_cache(cache_key, result)
            return result
        else:
            logger.warning(f"data.gov.in API returned status {resp.status_code}")
            return []

    except Exception as e:
        logger.warning(f"data.gov.in MSP data fetch failed (non-fatal): {e}")
        return []


def get_relevant_gov_links(query: str) -> list[dict]:
    query_lower = query.lower()
    relevant = []

    for source in RELIABLE_GOV_SOURCES:
        score = 0
        for topic in source["topics"]:
            if topic in query_lower:
                score += 2
            for word in topic.split():
                if len(word) > 3 and word in query_lower:
                    score += 1

        if score > 0:
            relevant.append({
                "title": source["name"],
                "url": source["url"],
                "score": score,
            })

    relevant.sort(key=lambda x: x["score"], reverse=True)
    return [{"title": r["title"], "url": r["url"]} for r in relevant[:3]]


def enrich_query_context(query: str, crop: Optional[str] = None) -> str:
    parts = []

    if crop or any(kw in query.lower() for kw in ["msp", "price", "support price", "minimum"]):
        msp_data = fetch_msp_data(crop)
        if msp_data:
            msp_lines = []
            for item in msp_data[:5]:
                line = f"  {item['commodity']}"
                if item.get("variety"):
                    line += f" ({item['variety']})"
                if item.get("msp"):
                    line += f": ₹{item['msp']}/quintal"
                if item.get("year"):
                    line += f" ({item['year']})"
                msp_lines.append(line)
            parts.append("=== MSP DATA (data.gov.in) ===\n" + "\n".join(msp_lines))

    gov_links = get_relevant_gov_links(query)
    if gov_links:
        link_lines = [f"  {l['title']}: {l['url']}" for l in gov_links]
        parts.append("=== OFFICIAL GOVERNMENT PORTALS ===\n" + "\n".join(link_lines))

    return "\n\n".join(parts)
