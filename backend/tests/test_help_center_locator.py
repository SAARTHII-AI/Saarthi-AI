"""
Help Center Locator tests for Saarthi-AI backend.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.help_center_locator import (
    HelpCenterLocator,
    HelpCenter,
    _haversine_distance,
    help_center_locator,
)


@pytest.fixture
def locator():
    return HelpCenterLocator()


class TestHaversineDistance:
    def test_same_point_distance_zero(self):
        assert _haversine_distance(28.6139, 77.2090, 28.6139, 77.2090) == 0

    def test_known_distance_delhi_mumbai(self):
        distance = _haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
        assert 1100 < distance < 1250


class TestHelpCenterDataclass:
    def test_help_center_defaults(self):
        center = HelpCenter(name="Test", address="Addr", lat=0, lng=0, distance_km=0)
        assert center.phone is None
        assert center.opening_hours is None
        assert center.place_id is None
        assert center.source == "unknown"

    def test_help_center_to_dict(self):
        center = HelpCenter(
            name="Center",
            address="Address",
            lat=28.6,
            lng=77.2,
            distance_km=1.2,
            source="brightdata",
        )
        data = center.to_dict()
        assert data["name"] == "Center"
        assert data["source"] == "brightdata"


class TestBrightDataParsing:
    def test_parse_brightdata_place_valid(self, locator):
        candidate = {
            "name": "CSC Center Delhi",
            "address": "Connaught Place, New Delhi",
            "latitude": 28.6315,
            "longitude": 77.2167,
            "phone": "+91-11-12345678",
            "id": "place_123",
            "opening_hours": ["Mon-Fri: 9-5"],
        }
        result = locator._parse_brightdata_place(candidate, 28.6139, 77.2090)
        assert result is not None
        assert result.name == "CSC Center Delhi"
        assert result.source == "brightdata"
        assert result.place_id == "place_123"
        assert result.distance_km > 0

    def test_parse_brightdata_place_missing_coordinates(self, locator):
        candidate = {"name": "No Coordinates"}
        assert locator._parse_brightdata_place(candidate, 28.6139, 77.2090) is None

    def test_parse_brightdata_place_generated_id(self, locator):
        candidate = {
            "name": "Generated ID Center",
            "address": "Delhi",
            "lat": 28.6315,
            "lng": 77.2167,
        }
        result = locator._parse_brightdata_place(candidate, 28.6139, 77.2090)
        assert result is not None
        assert result.place_id.startswith("bd_")

    def test_iter_candidates_handles_multiple_shapes(self, locator):
        payload = {
            "places": [{"name": "A"}],
            "local_results": [{"name": "B"}],
            "results": {"results": [{"name": "C"}]},
            "organic": [{"name": "D"}],
        }
        candidates = locator._iter_brightdata_candidates(payload)
        assert len(candidates) == 4


class TestFindNearbyCenters:
    @pytest.mark.asyncio
    async def test_find_nearby_returns_empty_when_unconfigured(self, locator):
        with patch("app.services.help_center_locator.settings") as mock_settings:
            mock_settings.offline_only = False
            mock_settings.brightdata_serp_configured.return_value = False
            results = await locator.find_nearby_centers(28.6139, 77.2090)
            assert results == []

    @pytest.mark.asyncio
    async def test_find_nearby_returns_brightdata_results(self, locator):
        with patch("app.services.help_center_locator.settings") as mock_settings:
            mock_settings.offline_only = False
            mock_settings.brightdata_serp_configured.return_value = True
            with patch.object(locator, "_search_brightdata_places", new_callable=AsyncMock) as mock_search:
                mock_search.return_value = [
                    HelpCenter(
                        name="Center",
                        address="Address",
                        lat=28.6315,
                        lng=77.2167,
                        distance_km=1.5,
                        source="brightdata",
                    )
                ]
                results = await locator.find_nearby_centers(28.6139, 77.2090, limit=5)
                assert len(results) == 1
                assert results[0].source == "brightdata"

    @pytest.mark.asyncio
    async def test_search_brightdata_places_filters_and_sorts(self, locator):
        with patch("app.services.help_center_locator.settings") as mock_settings:
            mock_settings.brightdata_api_token = "token"
            mock_settings.brightdata_serp_zone = "zone"
            mock_settings.brightdata_request_url = "https://api.brightdata.com/request"
            mock_settings.brightdata_serp_timeout_seconds = 5

            response_payload = {
                "places": [
                    {"name": "Far", "lat": 29.0, "lng": 77.2167, "id": "far"},
                    {"name": "Near", "lat": 28.6315, "lng": 77.2167, "id": "near"},
                ]
            }
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = response_payload
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response

            with patch.object(locator, "_get_client", new_callable=AsyncMock) as mock_get_client:
                mock_get_client.return_value = mock_client
                results = await locator._search_brightdata_places(28.6139, 77.2090, 5000, 10)
                assert [c.place_id for c in results] == ["near"]


class TestGetCenterDetails:
    @pytest.mark.asyncio
    async def test_get_details_from_cache(self, locator):
        center = HelpCenter(
            name="Cached",
            address="Addr",
            lat=28.6,
            lng=77.2,
            distance_km=1.0,
            place_id="cached_1",
            source="brightdata",
        )
        locator._details_cache["cached_1"] = center
        with patch("app.services.help_center_locator.settings") as mock_settings:
            mock_settings.offline_only = False
            mock_settings.brightdata_serp_configured.return_value = True
            result = await locator.get_center_details("cached_1")
            assert result is center

    @pytest.mark.asyncio
    async def test_get_details_unavailable_when_offline(self, locator):
        with patch("app.services.help_center_locator.settings") as mock_settings:
            mock_settings.offline_only = True
            mock_settings.brightdata_serp_configured.return_value = True
            assert await locator.get_center_details("any") is None

    @pytest.mark.asyncio
    async def test_get_brightdata_center_details(self, locator):
        with patch("app.services.help_center_locator.settings") as mock_settings:
            mock_settings.brightdata_api_token = "token"
            mock_settings.brightdata_serp_zone = "zone"
            mock_settings.brightdata_request_url = "https://api.brightdata.com/request"
            mock_settings.brightdata_serp_timeout_seconds = 5

            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "places": [
                    {
                        "id": "place_123",
                        "name": "Center",
                        "lat": 28.6315,
                        "lng": 77.2167,
                    }
                ]
            }
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            with patch.object(locator, "_get_client", new_callable=AsyncMock) as mock_get_client:
                mock_get_client.return_value = mock_client
                result = await locator._get_brightdata_center_details("place_123")
                assert result is not None
                assert result.place_id == "place_123"
                assert result.source == "brightdata"
                assert result.distance_km == 0


class TestGlobalInstance:
    def test_global_instance_exists(self):
        assert help_center_locator is not None
        assert isinstance(help_center_locator, HelpCenterLocator)
