import asyncio
from typing import Optional
from fastapi import APIRouter, Query
from ..models.listing import Listing, SearchRequest, SearchResponse
from ..mock_data import MOCK_LISTINGS, filter_mock
from ..config import settings

router = APIRouter()


def _get_ai_client():
    if not settings.anthropic_api_key:
        return None
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.anthropic_api_key)


@router.get("/listings", response_model=list[Listing])
async def get_listings(
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    bedrooms: Optional[int] = Query(None),
    district: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
):
    """Fetch listings (mock data for now, real scrapers coming soon)."""
    listings = filter_mock(
        MOCK_LISTINGS,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        district=district,
        property_type=property_type,
    )
    return sorted(listings, key=lambda l: l.price)


@router.post("/search", response_model=SearchResponse)
async def ai_search(request: SearchRequest):
    """Search listings; uses AI ranking if ANTHROPIC_API_KEY is set, otherwise keyword match."""
    client = _get_ai_client()

    # Extract structured filters via AI if available
    filters: dict = {}
    if client:
        from ..ai.filter import extract_filters
        filters = await extract_filters(request.query, client)

    min_price = request.min_price or filters.get("min_price")
    max_price = request.max_price or filters.get("max_price")
    bedrooms = request.bedrooms or filters.get("bedrooms")
    district = request.district or filters.get("district")
    property_type = request.property_type or filters.get("property_type")

    listings = filter_mock(
        MOCK_LISTINGS,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        district=district,
        property_type=property_type,
    )

    if not listings:
        return SearchResponse(listings=[], total=0, ai_summary="No listings found. Try broadening your search.")

    if client:
        from ..ai.filter import rank_listings
        ranked, summary = await rank_listings(listings, request, client)
    else:
        ranked = sorted(listings, key=lambda l: l.price)
        summary = "Showing mock data sorted by price. Add ANTHROPIC_API_KEY for AI-powered search."

    return SearchResponse(listings=ranked, total=len(ranked), ai_summary=summary)
