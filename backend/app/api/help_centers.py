"""
Help Centers API Router

Endpoints for finding nearby government service centers.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.help_center_locator import help_center_locator, HelpCenter

router = APIRouter()


class NearbyRequest(BaseModel):
    """Request model for finding nearby help centers."""
    lat: float = Field(..., description="Latitude of the search location", ge=-90, le=90)
    lng: float = Field(..., description="Longitude of the search location", ge=-180, le=180)
    radius_meters: int = Field(
        default=5000,
        description="Search radius in meters (default: 5000m = 5km)",
        ge=100,
        le=50000,
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=50,
    )


class HelpCenterResponse(BaseModel):
    """Response model for a single help center."""
    name: str
    address: str
    lat: float
    lng: float
    distance_km: float
    phone: Optional[str] = None
    opening_hours: Optional[List[str]] = None
    place_id: Optional[str] = None
    source: str


class NearbyResponse(BaseModel):
    """Response model for nearby help centers search."""
    centers: List[HelpCenterResponse]
    total: int
    search_location: dict
    radius_meters: int


class DetailsResponse(BaseModel):
    """Response model for help center details."""
    center: Optional[HelpCenterResponse] = None
    found: bool
    message: str


def _help_center_to_response(center: HelpCenter) -> HelpCenterResponse:
    """Convert a HelpCenter dataclass to a response model."""
    return HelpCenterResponse(
        name=center.name,
        address=center.address,
        lat=center.lat,
        lng=center.lng,
        distance_km=center.distance_km,
        phone=center.phone,
        opening_hours=center.opening_hours,
        place_id=center.place_id,
        source=center.source,
    )


@router.post("/nearby", response_model=NearbyResponse)
async def find_nearby_centers(request: NearbyRequest):
    """
    Find nearby government service centers.

    Searches for CSC Centers, e-Seva Kendras, Gram Panchayat offices,
    Tehsil offices, and other government service points near the
    specified location.

    Uses BrightData SERP data when configured.
    """
    try:
        centers = await help_center_locator.find_nearby_centers(
            lat=request.lat,
            lng=request.lng,
            radius_meters=request.radius_meters,
            limit=request.limit,
        )

        return NearbyResponse(
            centers=[_help_center_to_response(c) for c in centers],
            total=len(centers),
            search_location={"lat": request.lat, "lng": request.lng},
            radius_meters=request.radius_meters,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search for nearby centers: {str(exc)}",
        )


@router.get("/details/{place_id}", response_model=DetailsResponse)
async def get_center_details(place_id: str):
    """
    Get detailed information about a specific help center.

    Provide the place_id from a previous search result to get
    additional details like phone number and opening hours.
    """
    try:
        center = await help_center_locator.get_center_details(place_id)

        if center:
            return DetailsResponse(
                center=_help_center_to_response(center),
                found=True,
                message="Help center details retrieved successfully.",
            )
        else:
            return DetailsResponse(
                center=None,
                found=False,
                message="Help center not found. The place_id may be invalid or the service may be unavailable.",
            )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve center details: {str(exc)}",
        )
