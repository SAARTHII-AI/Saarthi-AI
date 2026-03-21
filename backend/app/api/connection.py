"""
Connection Status API Router

Endpoints for monitoring connection status and service health.
"""
from fastapi import APIRouter

from app.services.connection_manager import connection_manager

router = APIRouter()


@router.get("/status")
async def get_connection_status():
    """
    Get the current connection status and service health.

    Returns:
    - mode: "online", "offline", or "degraded"
    - forced_offline: Whether OFFLINE_ONLY is set to true
    - services: Health status of each service
    """
    return connection_manager.get_state()


@router.post("/health-check")
async def run_health_check():
    """
    Trigger a health check on all configured services.

    This will update the connection mode based on service availability.
    """
    state = await connection_manager.run_health_checks()
    return {
        "message": "Health check completed",
        "state": state,
    }


@router.get("/mode")
async def get_connection_mode():
    """
    Get just the current connection mode.

    Simplified endpoint for quick mode checks.
    """
    return {
        "mode": connection_manager.mode.value,
        "is_online": connection_manager.is_online,
    }
