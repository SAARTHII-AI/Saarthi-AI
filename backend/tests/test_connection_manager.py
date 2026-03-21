"""
Connection Manager tests for Saarthi-AI backend.

Tests cover:
- Service health recording
- Mode switching (online/offline/degraded)
- Recovery after failures
- Forced offline mode
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.connection_manager import (
    ConnectionManager,
    ConnectionMode,
    ServiceStatus,
    ServiceHealth,
    ConnectionState,
    should_use_online_services,
    get_service_status,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def fresh_connection_manager():
    """Create a fresh ConnectionManager instance for each test."""
    with patch('app.services.connection_manager.settings') as mock_settings:
        mock_settings.offline_only = False
        mock_settings.azure_openai_configured.return_value = True
        mock_settings.brightdata_serp_configured.return_value = True
        mock_settings.azure_speech_configured.return_value = True
        mock_settings.azure_openai_endpoint = "https://test.openai.azure.com"
        mock_settings.azure_openai_api_key = "test-key"
        mock_settings.azure_openai_api_version = "2024-02-15-preview"
        mock_settings.brightdata_api_token = "test-token"

        manager = ConnectionManager()
        yield manager


@pytest.fixture
def offline_connection_manager():
    """Create a ConnectionManager in forced offline mode."""
    with patch('app.services.connection_manager.settings') as mock_settings:
        mock_settings.offline_only = True
        mock_settings.azure_openai_configured.return_value = False
        mock_settings.brightdata_serp_configured.return_value = False
        mock_settings.azure_speech_configured.return_value = False

        manager = ConnectionManager()
        yield manager


# ============================================================================
# Connection Mode Tests
# ============================================================================

class TestConnectionMode:
    """Test connection mode enum and basic mode functionality."""

    def test_connection_mode_values(self):
        """Test that ConnectionMode has expected values."""
        assert ConnectionMode.ONLINE.value == "online"
        assert ConnectionMode.OFFLINE.value == "offline"
        assert ConnectionMode.DEGRADED.value == "degraded"

    def test_mode_property_online(self, fresh_connection_manager):
        """Test mode property returns online by default."""
        assert fresh_connection_manager.mode == ConnectionMode.ONLINE

    def test_mode_property_forced_offline(self, offline_connection_manager):
        """Test mode property returns offline when forced."""
        assert offline_connection_manager.mode == ConnectionMode.OFFLINE

    def test_is_online_property(self, fresh_connection_manager):
        """Test is_online property."""
        assert fresh_connection_manager.is_online is True

    def test_is_online_when_offline(self, offline_connection_manager):
        """Test is_online returns False when offline."""
        assert offline_connection_manager.is_online is False


# ============================================================================
# Service Status Tests
# ============================================================================

class TestServiceStatus:
    """Test service status enum and functionality."""

    def test_service_status_values(self):
        """Test that ServiceStatus has expected values."""
        assert ServiceStatus.HEALTHY.value == "healthy"
        assert ServiceStatus.DEGRADED.value == "degraded"
        assert ServiceStatus.UNHEALTHY.value == "unhealthy"
        assert ServiceStatus.UNCONFIGURED.value == "unconfigured"


# ============================================================================
# Service Health Recording Tests
# ============================================================================

class TestServiceHealthRecording:
    """Test service health recording functionality."""

    @pytest.mark.asyncio
    async def test_record_success(self, fresh_connection_manager):
        """Test recording a successful service call."""
        await fresh_connection_manager.record_success("azure_openai", response_time_ms=100)

        health = fresh_connection_manager._state.services["azure_openai"]
        assert health.status == ServiceStatus.HEALTHY
        assert health.consecutive_failures == 0
        assert health.last_error is None
        assert health.response_time_ms == 100

    @pytest.mark.asyncio
    async def test_record_success_resets_failures(self, fresh_connection_manager):
        """Test that success resets consecutive failures."""
        # First record some failures
        await fresh_connection_manager.record_failure("azure_openai", "Test error")
        await fresh_connection_manager.record_failure("azure_openai", "Test error")

        health = fresh_connection_manager._state.services["azure_openai"]
        assert health.consecutive_failures == 2

        # Now record success
        await fresh_connection_manager.record_success("azure_openai")

        assert health.consecutive_failures == 0
        assert health.status == ServiceStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_record_failure_increments_count(self, fresh_connection_manager):
        """Test that failure increments consecutive failures."""
        await fresh_connection_manager.record_failure("azure_openai", "Error 1")

        health = fresh_connection_manager._state.services["azure_openai"]
        assert health.consecutive_failures == 1
        assert health.status == ServiceStatus.DEGRADED
        assert health.last_error == "Error 1"

    @pytest.mark.asyncio
    async def test_record_failure_marks_unhealthy(self, fresh_connection_manager):
        """Test that max failures marks service unhealthy."""
        for i in range(ConnectionManager.MAX_CONSECUTIVE_FAILURES):
            await fresh_connection_manager.record_failure("azure_openai", f"Error {i}")

        health = fresh_connection_manager._state.services["azure_openai"]
        assert health.status == ServiceStatus.UNHEALTHY
        assert health.consecutive_failures >= ConnectionManager.MAX_CONSECUTIVE_FAILURES

    @pytest.mark.asyncio
    async def test_record_unknown_service(self, fresh_connection_manager):
        """Test recording for unknown service (should not raise)."""
        await fresh_connection_manager.record_success("unknown_service")
        await fresh_connection_manager.record_failure("unknown_service", "Error")
        # Should not raise


# ============================================================================
# Mode Switching Tests
# ============================================================================

class TestModeSwitching:
    """Test automatic mode switching based on service health."""

    @pytest.mark.asyncio
    async def test_switch_to_degraded_on_failure(self, fresh_connection_manager):
        """Test switching to degraded mode on service failure."""
        # Mark one service as unhealthy
        for _ in range(ConnectionManager.MAX_CONSECUTIVE_FAILURES):
            await fresh_connection_manager.record_failure("azure_openai", "Error")

        # Mode should be degraded (not all services down)
        assert fresh_connection_manager.mode in [ConnectionMode.DEGRADED, ConnectionMode.ONLINE]

    @pytest.mark.asyncio
    async def test_switch_to_offline_when_all_unhealthy(self, fresh_connection_manager):
        """Test switching to offline when all services are unhealthy."""
        services = ["azure_openai", "brightdata_serp", "azure_speech", "internet"]

        for service in services:
            for _ in range(ConnectionManager.MAX_CONSECUTIVE_FAILURES):
                await fresh_connection_manager.record_failure(service, "Error")

        # Should switch to offline mode
        assert fresh_connection_manager._state.mode == ConnectionMode.OFFLINE

    @pytest.mark.asyncio
    async def test_recovery_on_success(self, fresh_connection_manager):
        """Test recovery from degraded/offline on service success."""
        # First mark services unhealthy
        for _ in range(ConnectionManager.MAX_CONSECUTIVE_FAILURES):
            await fresh_connection_manager.record_failure("azure_openai", "Error")

        # Then record success
        await fresh_connection_manager.record_success("azure_openai")

        health = fresh_connection_manager._state.services["azure_openai"]
        assert health.status == ServiceStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_internet_down_forces_offline(self, fresh_connection_manager):
        """Test that internet failure forces offline mode."""
        for _ in range(ConnectionManager.MAX_CONSECUTIVE_FAILURES):
            await fresh_connection_manager.record_failure("internet", "No connectivity")

        assert fresh_connection_manager._state.services["internet"].status == ServiceStatus.UNHEALTHY


# ============================================================================
# Forced Offline Mode Tests
# ============================================================================

class TestForcedOfflineMode:
    """Test forced offline mode functionality."""

    def test_forced_offline_mode(self, offline_connection_manager):
        """Test that forced offline mode overrides everything."""
        assert offline_connection_manager._state.forced_offline is True
        assert offline_connection_manager.mode == ConnectionMode.OFFLINE

    def test_forced_offline_service_availability(self, offline_connection_manager):
        """Test that no services are available in forced offline mode."""
        assert offline_connection_manager.service_available("azure_openai") is False
        assert offline_connection_manager.service_available("brightdata_serp") is False

    @pytest.mark.asyncio
    async def test_forced_offline_ignores_updates(self, offline_connection_manager):
        """Test that forced offline mode ignores status updates."""
        await offline_connection_manager.record_success("azure_openai")

        # Still offline
        assert offline_connection_manager.mode == ConnectionMode.OFFLINE


# ============================================================================
# Service Availability Tests
# ============================================================================

class TestServiceAvailability:
    """Test service availability checks."""

    def test_service_available_healthy(self, fresh_connection_manager):
        """Test service availability when healthy."""
        assert fresh_connection_manager.service_available("azure_openai") is True

    def test_service_available_degraded(self, fresh_connection_manager):
        """Test service availability when degraded."""
        fresh_connection_manager._state.services["azure_openai"].status = ServiceStatus.DEGRADED
        assert fresh_connection_manager.service_available("azure_openai") is True

    def test_service_available_unhealthy(self, fresh_connection_manager):
        """Test service availability when unhealthy."""
        fresh_connection_manager._state.services["azure_openai"].status = ServiceStatus.UNHEALTHY
        assert fresh_connection_manager.service_available("azure_openai") is False

    def test_service_available_unconfigured(self, fresh_connection_manager):
        """Test service availability when unconfigured."""
        fresh_connection_manager._state.services["azure_openai"].status = ServiceStatus.UNCONFIGURED
        assert fresh_connection_manager.service_available("azure_openai") is False

    def test_service_available_unknown_service(self, fresh_connection_manager):
        """Test availability of unknown service."""
        assert fresh_connection_manager.service_available("unknown_service") is False


# ============================================================================
# State Retrieval Tests
# ============================================================================

class TestStateRetrieval:
    """Test connection state retrieval."""

    def test_get_state_structure(self, fresh_connection_manager):
        """Test that get_state returns correct structure."""
        state = fresh_connection_manager.get_state()

        assert "mode" in state
        assert "forced_offline" in state
        assert "services" in state
        assert "auto_recovery_enabled" in state

    def test_get_state_services_structure(self, fresh_connection_manager):
        """Test that services in state have correct structure."""
        state = fresh_connection_manager.get_state()

        for service_name, service_info in state["services"].items():
            assert "name" in service_info
            assert "status" in service_info
            assert "last_check" in service_info
            assert "consecutive_failures" in service_info
            assert "last_error" in service_info
            assert "response_time_ms" in service_info

    def test_get_state_mode_value(self, fresh_connection_manager):
        """Test that mode is a string value."""
        state = fresh_connection_manager.get_state()
        assert state["mode"] in ["online", "offline", "degraded"]


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthChecks:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_check_internet_connectivity_success(self, fresh_connection_manager):
        """Test internet connectivity check success."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await fresh_connection_manager.check_internet_connectivity()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_internet_connectivity_failure(self, fresh_connection_manager):
        """Test internet connectivity check failure."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = Exception("Connection error")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await fresh_connection_manager.check_internet_connectivity()
            assert result is False

    @pytest.mark.asyncio
    async def test_run_health_checks_rate_limiting(self, fresh_connection_manager):
        """Test that health checks respect rate limiting."""
        fresh_connection_manager._last_health_check = time.time()

        # Mock the check methods
        with patch.object(fresh_connection_manager, 'check_internet_connectivity', new_callable=AsyncMock) as mock:
            mock.return_value = True
            await fresh_connection_manager.run_health_checks()

            # Should not call check due to rate limiting
            mock.assert_not_called()


# ============================================================================
# Global Function Tests
# ============================================================================

class TestGlobalFunctions:
    """Test module-level utility functions."""

    def test_should_use_online_services(self):
        """Test should_use_online_services function."""
        with patch('app.services.connection_manager.connection_manager') as mock_manager:
            mock_manager.is_online = True
            assert should_use_online_services() is True

            mock_manager.is_online = False
            assert should_use_online_services() is False

    def test_get_service_status(self):
        """Test get_service_status function."""
        with patch('app.services.connection_manager.connection_manager') as mock_manager:
            mock_health = ServiceHealth(
                name="Azure OpenAI",
                status=ServiceStatus.HEALTHY
            )
            mock_manager._state.services = {"azure_openai": mock_health}

            status = get_service_status("azure_openai")
            assert status == ServiceStatus.HEALTHY

    def test_get_service_status_unknown(self):
        """Test get_service_status for unknown service."""
        with patch('app.services.connection_manager.connection_manager') as mock_manager:
            mock_manager._state.services = {}

            status = get_service_status("unknown_service")
            assert status == ServiceStatus.UNCONFIGURED


# ============================================================================
# Dataclass Tests
# ============================================================================

class TestDataclasses:
    """Test dataclass structures."""

    def test_service_health_defaults(self):
        """Test ServiceHealth default values."""
        health = ServiceHealth(name="Test", status=ServiceStatus.HEALTHY)

        assert health.last_check == 0
        assert health.consecutive_failures == 0
        assert health.last_error is None
        assert health.response_time_ms is None

    def test_connection_state_defaults(self):
        """Test ConnectionState default values."""
        state = ConnectionState()

        assert state.mode == ConnectionMode.ONLINE
        assert state.forced_offline is False
        assert state.services == {}
        assert state.last_mode_change == 0
        assert state.auto_recovery_enabled is True


# ============================================================================
# Configuration Constants Tests
# ============================================================================

class TestConfigurationConstants:
    """Test configuration constants."""

    def test_max_consecutive_failures(self):
        """Test MAX_CONSECUTIVE_FAILURES constant."""
        assert ConnectionManager.MAX_CONSECUTIVE_FAILURES == 3

    def test_health_check_interval(self):
        """Test HEALTH_CHECK_INTERVAL_SECONDS constant."""
        assert ConnectionManager.HEALTH_CHECK_INTERVAL_SECONDS == 60

    def test_recovery_check_interval(self):
        """Test RECOVERY_CHECK_INTERVAL_SECONDS constant."""
        assert ConnectionManager.RECOVERY_CHECK_INTERVAL_SECONDS == 30

    def test_timeout_seconds(self):
        """Test TIMEOUT_SECONDS constant."""
        assert ConnectionManager.TIMEOUT_SECONDS == 10


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_concurrent_health_updates(self, fresh_connection_manager):
        """Test concurrent health updates don't cause race conditions."""
        tasks = []
        for i in range(10):
            if i % 2 == 0:
                tasks.append(fresh_connection_manager.record_success("azure_openai", i * 10))
            else:
                tasks.append(fresh_connection_manager.record_failure("azure_openai", f"Error {i}"))

        await asyncio.gather(*tasks)
        # Should complete without errors

    def test_services_initialization(self, fresh_connection_manager):
        """Test that all expected services are initialized."""
        expected_services = ["azure_openai", "brightdata_serp", "azure_speech", "internet"]

        for service in expected_services:
            assert service in fresh_connection_manager._state.services

    @pytest.mark.asyncio
    async def test_update_connection_mode_no_configured_services(self, fresh_connection_manager):
        """Test mode update when no services are configured."""
        # Mark all services as unconfigured
        for service in fresh_connection_manager._state.services.values():
            service.status = ServiceStatus.UNCONFIGURED

        await fresh_connection_manager._update_connection_mode()
        assert fresh_connection_manager._state.mode == ConnectionMode.OFFLINE
