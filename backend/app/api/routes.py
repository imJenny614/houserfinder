import asyncio
import json
import logging
from typing import Optional
from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)
from ..models.listing import Listing, SearchRequest, SearchResponse
from ..scrapers import PropertyGuruScraper, NinetyNineScraper
from ..mock_data import MOCK_LISTINGS, filter_mock
from ..cache import get as cache_get, set as cache_set
from ..config import settings

router = APIRouter()

_scrapers = [PropertyGuruScraper(), NinetyNineScraper()]


def _get_ai_client():
    if not settings.anthropic_api_key:
        return None
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.anthropic_api_key)


def _cache_key(**kwargs) -> str:
    return json.dumps(kwargs, sort_keys=True)


async def _fetch_listings(
    min_price=None, max_price=None, bedrooms=None,
    district=None, property_type=None, page=1,
) -> list[Listing]:
    """Fetch from real scrapers with cache; fall back to mock data if empty."""
    key = _cache_key(
        min_price=min_price, max_price=max_price, bedrooms=bedrooms,
        district=district, property_type=property_type, page=page,
    )
    cached = cache_get(key)
    if cached is not None:
        return cached

    tasks = [
        scraper.search(
            min_price=min_price, max_price=max_price, bedrooms=bedrooms,
            district=district, property_type=property_type, page=page,
        )
        for scraper in _scrapers
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    listings: list[Listing] = []
    for result in results:
        if isinstance(result, list):
            listings.extend(result)

    if not listings:
        logger.warning("All scrapers returned empty — falling back to mock data")
        listings = filter_mock(
            MOCK_LISTINGS,
            min_price=min_price, max_price=max_price,
            bedrooms=bedrooms, district=district, property_type=property_type,
        )

    listings = sorted(listings, key=lambda l: l.price)
    cache_set(key, listings)
    return listings


@router.get("/listings", response_model=list[Listing])
async def get_listings(
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    bedrooms: Optional[int] = Query(None),
    district: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
):
    return await _fetch_listings(
        min_price=min_price, max_price=max_price, bedrooms=bedrooms,
        district=district, property_type=property_type, page=page,
    )


@router.get("/debug/scrape")
async def debug_scrape():
    """Test each scraper independently and return raw results + errors."""
    results = {}
    for scraper in _scrapers:
        try:
            items = await scraper.search()
            results[scraper.source_name] = {
                "count": len(items),
                "sample": [i.model_dump() for i in items[:2]],
                "error": None,
            }
        except Exception as e:
            results[scraper.source_name] = {"count": 0, "sample": [], "error": str(e)}
    return results


@router.get("/debug/page")
async def debug_page(url: str = Query(...)):
    """Load a URL in Playwright and return title, final URL, selector counts, and HTML snippet."""
    from ..scrapers.browser import get_browser, new_context
    import base64

    browser = await get_browser()
    ctx = await new_context(browser)
    try:
        pg = await ctx.new_page()
        await pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        await pg.wait_for_timeout(3000)

        title = await pg.title()
        final_url = pg.url
        html_snippet = (await pg.content())[:3000]

        # Count how many elements match various selectors
        selector_counts = await pg.evaluate("""() => {
            const selectors = [
                '[data-listing-id]',
                '.listing-card',
                '.property-card',
                'a[href*="/rent/"]',
                'a[href*="for-rent"]',
                '[class*="listing"]',
                '[class*="property"]',
                '[class*="price"]',
            ];
            const result = {};
            for (const sel of selectors) {
                result[sel] = document.querySelectorAll(sel).length;
            }
            return result;
        }""")

        # Take a screenshot and return as base64
        screenshot = await pg.screenshot(type="jpeg", quality=60)
        screenshot_b64 = base64.b64encode(screenshot).decode()

        return {
            "title": title,
            "final_url": final_url,
            "selector_counts": selector_counts,
            "html_snippet": html_snippet,
            "screenshot_base64": screenshot_b64,
        }
    finally:
        await ctx.close()


@router.post("/search", response_model=SearchResponse)
async def ai_search(request: SearchRequest):
    client = _get_ai_client()

    filters: dict = {}
    if client:
        from ..ai.filter import extract_filters
        filters = await extract_filters(request.query, client)

    min_price = request.min_price or filters.get("min_price")
    max_price = request.max_price or filters.get("max_price")
    bedrooms = request.bedrooms or filters.get("bedrooms")
    district = request.district or filters.get("district")
    property_type = request.property_type or filters.get("property_type")

    listings = await _fetch_listings(
        min_price=min_price, max_price=max_price, bedrooms=bedrooms,
        district=district, property_type=property_type,
    )

    if not listings:
        return SearchResponse(listings=[], total=0, ai_summary="No listings found.")

    if client:
        from ..ai.filter import rank_listings
        ranked, summary = await rank_listings(listings, request, client)
    else:
        ranked = listings
        summary = "Showing results sorted by price. Add ANTHROPIC_API_KEY for AI-powered ranking."

    return SearchResponse(listings=ranked, total=len(ranked), ai_summary=summary)
