"""
Connection Manager for Auto-Switch between Online and Offline modes.

Monitors service health and automatically switches to offline mode when
online services are unavailable or failing.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ConnectionMode(str, Enum):
    """Current connection mode."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"  # Some services available, some not


class ServiceStatus(str, Enum):
    """Status of an individual service."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNCONFIGURED = "unconfigured"


@dataclass
class ServiceHealth:
    """Health information for a single service."""
    name: str
    status: ServiceStatus
    last_check: float = 0
    consecutive_failures: int = 0
    last_error: Optional[str] = None
    response_time_ms: Optional[float] = None


@dataclass
class ConnectionState:
    """Overall connection state."""
    mode: ConnectionMode = ConnectionMode.ONLINE
    forced_offline: bool = False  # User explicitly set OFFLINE_ONLY=true
    services: Dict[str, ServiceHealth] = field(default_factory=dict)
    last_mode_change: float = 0
    auto_recovery_enabled: bool = True


class ConnectionManager:
    """
    Manages connection state and auto-switching between online/offline modes.

    Features:
    - Health checks for configured services
    - Automatic fallback to offline mode after consecutive failures
    - Auto-recovery when services become available again
    - Graceful degradation (some services may work while others don't)
    """

    # Configuration
    MAX_CONSECUTIVE_FAILURES = 3  # Switch to offline after this many failures
    HEALTH_CHECK_INTERVAL_SECONDS = 60  # How often to check service health
    RECOVERY_CHECK_INTERVAL_SECONDS = 30  # How often to check for recovery when offline
    TIMEOUT_SECONDS = 10  # Timeout for health check requests

    def __init__(self):
        self._state = ConnectionState(
            forced_offline=settings.offline_only
        )
        self._lock = asyncio.Lock()
        self._last_health_check: float = 0

        # Initialize service health entries
        self._init_services()

    def _init_services(self) -> None:
        """Initialize service health tracking."""
        services = {
            "azure_openai": ServiceHealth(
                name="Azure OpenAI",
                status=ServiceStatus.UNCONFIGURED if not settings.azure_openai_configured() else ServiceStatus.HEALTHY
            ),
            "brightdata_serp": ServiceHealth(
                name="BrightData SERP",
                status=ServiceStatus.UNCONFIGURED if not settings.brightdata_serp_configured() else ServiceStatus.HEALTHY
            ),
            "azure_speech": ServiceHealth(
                name="Azure Speech",
                status=ServiceStatus.UNCONFIGURED if not settings.azure_speech_configured() else ServiceStatus.HEALTHY
            ),
            "internet": ServiceHealth(
                name="Internet Connectivity",
                status=ServiceStatus.HEALTHY
            ),
        }
        self._state.services = services

    @property
    def mode(self) -> ConnectionMode:
        """Get current connection mode."""
        if self._state.forced_offline:
            return ConnectionMode.OFFLINE
        return self._state.mode

    @property
    def is_online(self) -> bool:
        """Check if we should use online services."""
        return self.mode != ConnectionMode.OFFLINE

    def get_state(self) -> dict:
        """Get the current connection state as a dictionary."""
        return {
            "mode": self.mode.value,
            "forced_offline": self._state.forced_offline,
            "services": {
                name: {
                    "name": health.name,
                    "status": health.status.value,
                    "last_check": health.last_check,
                    "consecutive_failures": health.consecutive_failures,
                    "last_error": health.last_error,
                    "response_time_ms": health.response_time_ms,
                }
                for name, health in self._state.services.items()
            },
            "auto_recovery_enabled": self._state.auto_recovery_enabled,
        }

    def service_available(self, service_name: str) -> bool:
        """Check if a specific service is available."""
        if self._state.forced_offline:
            return False

        health = self._state.services.get(service_name)
        if not health:
            return False

        return health.status in (ServiceStatus.HEALTHY, ServiceStatus.DEGRADED)

    async def record_success(self, service_name: str, response_time_ms: Optional[float] = None) -> None:
        """Record a successful service call."""
        async with self._lock:
            health = self._state.services.get(service_name)
            if health:
                health.status = ServiceStatus.HEALTHY
                health.consecutive_failures = 0
                health.last_error = None
                health.last_check = time.time()
                if response_time_ms is not None:
                    health.response_time_ms = response_time_ms

                # Check if we can switch back to online mode
                await self._check_mode_recovery()

    async def record_failure(self, service_name: str, error: Optional[str] = None) -> None:
        """Record a service call failure."""
        async with self._lock:
            health = self._state.services.get(service_name)
            if health:
                health.consecutive_failures += 1
                health.last_error = error
                health.last_check = time.time()

                # Update status based on failure count
                if health.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                    health.status = ServiceStatus.UNHEALTHY
                    logger.warning(
                        f"Service {service_name} marked unhealthy after "
                        f"{health.consecutive_failures} consecutive failures"
                    )
                else:
                    health.status = ServiceStatus.DEGRADED

                # Check if we need to switch to offline/degraded mode
                await self._update_connection_mode()

    async def _update_connection_mode(self) -> None:
        """Update the overall connection mode based on service health."""
        if self._state.forced_offline:
            return

        # Count healthy/unhealthy services (excluding unconfigured)
        configured_services = [
            h for h in self._state.services.values()
            if h.status != ServiceStatus.UNCONFIGURED
        ]

        if not configured_services:
            self._state.mode = ConnectionMode.OFFLINE
            return

        unhealthy_count = sum(
            1 for h in configured_services
            if h.status == ServiceStatus.UNHEALTHY
        )

        old_mode = self._state.mode

        # If internet is down, everything is offline
        internet_health = self._state.services.get("internet")
        if internet_health and internet_health.status == ServiceStatus.UNHEALTHY:
            self._state.mode = ConnectionMode.OFFLINE
        elif unhealthy_count == len(configured_services):
            self._state.mode = ConnectionMode.OFFLINE
        elif unhealthy_count > 0:
            self._state.mode = ConnectionMode.DEGRADED
        else:
            self._state.mode = ConnectionMode.ONLINE

        if old_mode != self._state.mode:
            self._state.last_mode_change = time.time()
            logger.info(f"Connection mode changed from {old_mode.value} to {self._state.mode.value}")

    async def _check_mode_recovery(self) -> None:
        """Check if we can recover from offline/degraded mode."""
        if not self._state.auto_recovery_enabled:
            return

        await self._update_connection_mode()

    async def check_internet_connectivity(self) -> bool:
        """Check basic internet connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
                start = time.time()
                # Try to reach a reliable endpoint
                response = await client.get("https://www.google.com/generate_204")
                response_time_ms = (time.time() - start) * 1000

                if response.status_code == 204:
                    await self.record_success("internet", response_time_ms)
                    return True
                else:
                    await self.record_failure("internet", f"Unexpected status: {response.status_code}")
                    return False
        except Exception as e:
            await self.record_failure("internet", str(e))
            return False

    async def run_health_checks(self) -> dict:
        """
        Run health checks on all configured services.
        Returns the updated state.
        """
        current_time = time.time()

        # Don't check too frequently
        if current_time - self._last_health_check < self.HEALTH_CHECK_INTERVAL_SECONDS:
            return self.get_state()

        self._last_health_check = current_time

        # Check internet first
        await self.check_internet_connectivity()

        # If internet is down, don't bother checking other services
        if self._state.services["internet"].status == ServiceStatus.UNHEALTHY:
            return self.get_state()

        # Check Azure OpenAI
        if settings.azure_openai_configured():
            await self._check_azure_openai()

        # Check BrightData
        if settings.brightdata_serp_configured():
            await self._check_brightdata()

        # Check Azure Speech
        if settings.azure_speech_configured():
            await self._check_azure_speech()

        return self.get_state()

    async def _check_azure_openai(self) -> None:
        """Health check for Azure OpenAI."""
        try:
            endpoint = settings.azure_openai_endpoint
            api_key = settings.azure_openai_api_key
            if not endpoint or not api_key:
                await self.record_failure("azure_openai", "Azure OpenAI not configured")
                return

            async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
                start = time.time()
                # Just check if the endpoint is reachable
                url = f"{endpoint}/openai/deployments?api-version={settings.azure_openai_api_version}"
                response = await client.get(
                    url,
                    headers={"api-key": api_key}
                )
                response_time_ms = (time.time() - start) * 1000

                if response.status_code in (200, 401, 403):  # Even auth errors mean service is reachable
                    await self.record_success("azure_openai", response_time_ms)
                else:
                    await self.record_failure("azure_openai", f"Status: {response.status_code}")
        except Exception as e:
            await self.record_failure("azure_openai", str(e))

    async def _check_brightdata(self) -> None:
        """Health check for BrightData."""
        try:
            token = settings.brightdata_api_token
            if not token:
                await self.record_failure("brightdata_serp", "BrightData not configured")
                return

            async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
                start = time.time()
                # Check BrightData API endpoint
                response = await client.get(
                    "https://api.brightdata.com/health",
                    headers={"Authorization": f"Bearer {token}"}
                )
                response_time_ms = (time.time() - start) * 1000

                if response.status_code in (200, 401, 403):
                    await self.record_success("brightdata_serp", response_time_ms)
                else:
                    await self.record_failure("brightdata_serp", f"Status: {response.status_code}")
        except Exception as e:
            await self.record_failure("brightdata_serp", str(e))

    async def _check_azure_speech(self) -> None:
        """Health check for Azure Speech."""
        try:
            key = settings.azure_speech_key
            region = settings.azure_speech_region
            if not key or not region:
                await self.record_failure("azure_speech", "Azure Speech not configured")
                return

            health_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
            async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
                start = time.time()
                response = await client.get(
                    health_url,
                    headers={"Ocp-Apim-Subscription-Key": key},
                )
                response_time_ms = (time.time() - start) * 1000

                if response.status_code in (200, 401, 403):
                    await self.record_success("azure_speech", response_time_ms)
                else:
                    await self.record_failure("azure_speech", f"Status: {response.status_code}")
        except Exception as e:
            await self.record_failure("azure_speech", str(e))

# Global singleton instance
connection_manager = ConnectionManager()


def should_use_online_services() -> bool:
    """
    Check if online services should be used.
    This is the main function to call before making online service calls.
    """
    return connection_manager.is_online


def get_service_status(service_name: str) -> ServiceStatus:
    """Get the health status of a specific service."""
    health = connection_manager._state.services.get(service_name)
    if health:
        return health.status
    return ServiceStatus.UNCONFIGURED
