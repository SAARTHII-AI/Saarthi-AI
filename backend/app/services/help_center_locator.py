"""
Help Center Locator Service

Finds nearby government service centers (CSC Centers, e-Seva Kendras, etc.)
using BrightData SERP data.
"""
from __future__ import annotations

import hashlib
import logging
import math
import time
from dataclasses import dataclass, asdict
from typing import List, Optional
from urllib.parse import quote_plus

import httpx

from app.config import settings
from app.services.connection_manager import (
    ServiceStatus,
    connection_manager,
    get_service_status,
    should_use_online_services,
)

logger = logging.getLogger(__name__)


@dataclass
class HelpCenter:
    """Represents a government service center / help center."""
    name: str
    address: str
    lat: float
    lng: float
    distance_km: float
    phone: Optional[str] = None
    opening_hours: Optional[List[str]] = None
    place_id: Optional[str] = None
    source: str = "unknown"

    def to_dict(self) -> dict:
        return asdict(self)


def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth (in km).
    """
    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


class HelpCenterLocator:
    """
    Service for finding nearby government help centers.

    Uses BrightData SERP API for lookup and details.
    """

    BRIGHTDATA_MAX_QUERY_VARIANTS = 4
    CSC_SEARCH_QUERIES = [
        "CSC Center",
        "Common Service Centre",
        "e-Seva Kendra",
        "Jan Seva Kendra",
        "Gram Panchayat Office",
        "Tehsil Office",
        "District Collector Office",
    ]

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._details_cache: dict[str, HelpCenter] = {}

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def find_nearby_centers(
        self,
        lat: float,
        lng: float,
        radius_meters: int = 5000,
        limit: int = 10,
    ) -> List[HelpCenter]:
        """
        Find nearby government service centers.

        Args:
            lat: Latitude of the search location
            lng: Longitude of the search location
            radius_meters: Search radius in meters (default: 5000m = 5km)
            limit: Maximum number of results to return

        Returns:
            List of HelpCenter objects sorted by distance
        """
        if settings.offline_only or not settings.brightdata_serp_configured():
            return []
        brightdata_status = get_service_status("brightdata_serp")
        service_blocked = (
            brightdata_status != ServiceStatus.UNCONFIGURED
            and not connection_manager.service_available("brightdata_serp")
        )
        if not should_use_online_services() or service_blocked:
            logger.info("BrightData service unavailable, skipping help center lookup")
            return []

        try:
            centers = await self._search_brightdata_places(lat, lng, radius_meters, limit)
            logger.info("Found %d centers via BrightData", len(centers))
            return centers[:limit]
        except Exception as exc:
            logger.warning("BrightData search failed: %s", exc)
            return []

    async def _search_brightdata_places(
        self,
        lat: float,
        lng: float,
        radius_meters: int,
        limit: int,
    ) -> List[HelpCenter]:
        """Search for help centers using BrightData SERP API."""
        client = await self._get_client()
        all_centers: List[HelpCenter] = []
        seen_place_ids: set[str] = set()
        radius_km = radius_meters / 1000

        headers = {
            "Authorization": f"Bearer {settings.brightdata_api_token}",
            "Content-Type": "application/json",
        }

        for query in self.CSC_SEARCH_QUERIES[: self.BRIGHTDATA_MAX_QUERY_VARIANTS]:
            if len(all_centers) >= limit * 2:
                break
            search_query = f"{query} near {lat},{lng} India within {radius_km:.1f} km"
            payload = {
                "zone": settings.brightdata_serp_zone,
                "url": f"https://www.google.com/search?q={quote_plus(search_query)}&hl=en&gl=in",
                "format": "raw",
                "data_format": "parsed_light",
            }
            try:
                start = time.time()
                response = await client.post(
                    settings.brightdata_request_url,
                    headers=headers,
                    json=payload,
                    timeout=httpx.Timeout(settings.brightdata_serp_timeout_seconds),
                )
                response.raise_for_status()
                response_time_ms = (time.time() - start) * 1000
                await connection_manager.record_success("brightdata_serp", response_time_ms)
                data = response.json()
                for candidate in self._iter_brightdata_candidates(data):
                    center = self._parse_brightdata_place(candidate, lat, lng)
                    if not center:
                        continue
                    if center.distance_km > radius_km:
                        continue
                    if center.place_id in seen_place_ids:
                        continue
                    if center.place_id:
                        seen_place_ids.add(center.place_id)
                        self._details_cache[center.place_id] = center
                    all_centers.append(center)
            except Exception as exc:
                await connection_manager.record_failure("brightdata_serp", str(exc))
                logger.warning("BrightData search failed for '%s': %s", query, exc)

        all_centers.sort(key=lambda c: c.distance_km)
        return all_centers

    def _iter_brightdata_candidates(self, payload: dict) -> List[dict]:
        candidates: List[dict] = []
        for key in ("places", "local_results", "results", "organic"):
            value = payload.get(key)
            if isinstance(value, list):
                candidates.extend([item for item in value if isinstance(item, dict)])
            elif isinstance(value, dict):
                nested = value.get("results")
                if isinstance(nested, list):
                    candidates.extend([item for item in nested if isinstance(item, dict)])
        return candidates

    def _extract_coordinates(self, place: dict) -> tuple[Optional[float], Optional[float]]:
        lat = place.get("lat") or place.get("latitude")
        lng = place.get("lng") or place.get("lon") or place.get("longitude")
        if lat is None or lng is None:
            gps = place.get("gps_coordinates") or place.get("coordinates")
            if isinstance(gps, dict):
                lat = gps.get("latitude") or gps.get("lat")
                lng = gps.get("longitude") or gps.get("lng") or gps.get("lon")
        try:
            if lat is None or lng is None:
                return None, None
            return float(lat), float(lng)
        except (TypeError, ValueError):
            return None, None

    def _build_place_id(self, place: dict, name: str, address: str, lat: float, lng: float) -> str:
        raw_id = place.get("place_id") or place.get("id") or place.get("cid")
        if raw_id:
            return str(raw_id)
        fingerprint = f"{name}|{address}|{lat:.6f}|{lng:.6f}"
        digest = hashlib.md5(fingerprint.encode("utf-8")).hexdigest()[:16]
        return f"bd_{digest}"

    def _parse_opening_hours(self, place: dict) -> Optional[List[str]]:
        opening_hours = place.get("opening_hours")
        if isinstance(opening_hours, dict):
            weekday = opening_hours.get("weekday_text")
            if isinstance(weekday, list):
                return [str(item) for item in weekday]
        if isinstance(opening_hours, list):
            return [str(item) for item in opening_hours]
        if isinstance(opening_hours, str) and opening_hours.strip():
            return [opening_hours.strip()]
        return None

    def _parse_brightdata_place(
        self,
        place: dict,
        origin_lat: Optional[float],
        origin_lng: Optional[float],
    ) -> Optional[HelpCenter]:
        """Parse a BrightData candidate into a HelpCenter object."""
        try:
            place_lat, place_lng = self._extract_coordinates(place)
            if place_lat is None or place_lng is None:
                return None

            if origin_lat is not None and origin_lng is not None:
                distance_km = _haversine_distance(origin_lat, origin_lng, place_lat, place_lng)
            else:
                distance_km = 0.0

            name = (
                place.get("name")
                or place.get("title")
                or place.get("place_name")
                or "Government Service Center"
            )
            address = (
                place.get("address")
                or place.get("formatted_address")
                or place.get("vicinity")
                or place.get("displayed_link")
                or "Address not available"
            )
            place_id = self._build_place_id(place, name, address, place_lat, place_lng)

            return HelpCenter(
                name=str(name),
                address=str(address),
                lat=place_lat,
                lng=place_lng,
                distance_km=round(distance_km, 2),
                phone=place.get("phone") or place.get("phone_number"),
                opening_hours=self._parse_opening_hours(place),
                place_id=place_id,
                source="brightdata",
            )
        except Exception as exc:
            logger.warning("Failed to parse BrightData place: %s", exc)
            return None

    async def get_center_details(self, place_id: str) -> Optional[HelpCenter]:
        """
        Get detailed information about a specific help center.

        Args:
            place_id: BrightData place identifier

        Returns:
            HelpCenter with detailed information, or None if not found
        """
        if settings.offline_only or not settings.brightdata_serp_configured():
            return None
        brightdata_status = get_service_status("brightdata_serp")
        service_blocked = (
            brightdata_status != ServiceStatus.UNCONFIGURED
            and not connection_manager.service_available("brightdata_serp")
        )
        if not should_use_online_services() or service_blocked:
            logger.info("BrightData service unavailable, skipping help center details lookup")
            return None
        if place_id in self._details_cache:
            return self._details_cache[place_id]
        return await self._get_brightdata_center_details(place_id)

    async def _get_brightdata_center_details(self, place_id: str) -> Optional[HelpCenter]:
        """Get detailed information for a center using BrightData SERP API."""
        client = await self._get_client()
        payload = {
            "zone": settings.brightdata_serp_zone,
            "url": (
                f"https://www.google.com/search?q={quote_plus(f'{place_id} government service center India')}"
                "&hl=en&gl=in"
            ),
            "format": "raw",
            "data_format": "parsed_light",
        }
        headers = {
            "Authorization": f"Bearer {settings.brightdata_api_token}",
            "Content-Type": "application/json",
        }

        try:
            start = time.time()
            response = await client.post(
                settings.brightdata_request_url,
                headers=headers,
                json=payload,
                timeout=httpx.Timeout(settings.brightdata_serp_timeout_seconds),
            )
            response.raise_for_status()
            response_time_ms = (time.time() - start) * 1000
            await connection_manager.record_success("brightdata_serp", response_time_ms)
            data = response.json()
            for candidate in self._iter_brightdata_candidates(data):
                parsed = self._parse_brightdata_place(candidate, None, None)
                if not parsed or parsed.place_id != place_id:
                    continue
                parsed.distance_km = 0
                self._details_cache[place_id] = parsed
                return parsed
        except Exception as exc:
            await connection_manager.record_failure("brightdata_serp", str(exc))
            logger.warning("Failed to get BrightData center details: %s", exc)
            return None
        return None


# Global instance for reuse
help_center_locator = HelpCenterLocator()
