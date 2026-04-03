import asyncio
from fastapi import APIRouter, Query, HTTPException
from anthropic import AsyncAnthropic
from ..models.listing import Listing, SearchRequest, SearchResponse
from ..scrapers import PropertyGuruScraper, NinetyNineScraper
from ..ai.filter import extract_filters, rank_listings
from ..config import settings

router = APIRouter()

_anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
_scrapers = [PropertyGuruScraper(), NinetyNineScraper()]


@router.get("/listings", response_model=list[Listing])
async def get_listings(
    min_price: int | None = Query(None),
    max_price: int | None = Query(None),
    bedrooms: int | None = Query(None),
    district: str | None = Query(None),
    property_type: str | None = Query(None),
    page: int = Query(1, ge=1),
):
    """Fetch raw listings from all sources with optional filters."""
    tasks = [
        scraper.search(
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            district=district,
            property_type=property_type,
            page=page,
        )
        for scraper in _scrapers
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    listings: list[Listing] = []
    for result in results:
        if isinstance(result, list):
            listings.extend(result)
    return sorted(listings, key=lambda l: l.price)


@router.post("/search", response_model=SearchResponse)
async def ai_search(request: SearchRequest):
    """AI-powered natural language search across all sources."""
    # Extract structured filters from query
    filters = await extract_filters(request.query, _anthropic_client)

    # Merge explicit params from request body over AI-extracted ones
    min_price = request.min_price or filters.get("min_price")
    max_price = request.max_price or filters.get("max_price")
    bedrooms = request.bedrooms or filters.get("bedrooms")
    district = request.district or filters.get("district")
    property_type = request.property_type or filters.get("property_type")

    # Fetch from all scrapers in parallel
    tasks = [
        scraper.search(
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            district=district,
            property_type=property_type,
        )
        for scraper in _scrapers
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    listings: list[Listing] = []
    for result in results:
        if isinstance(result, list):
            listings.extend(result)

    if not listings:
        return SearchResponse(listings=[], total=0, ai_summary="No listings found. Try broadening your search.")

    # AI ranking
    ranked, summary = await rank_listings(listings, request, _anthropic_client)

    return SearchResponse(listings=ranked, total=len(ranked), ai_summary=summary)
