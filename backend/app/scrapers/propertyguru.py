import hashlib
import asyncio
import logging
from typing import Optional
from .base import BaseScraper
from .browser import get_browser, new_context
from ..models.listing import Listing

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.propertyguru.com.sg/property-for-rent"


class PropertyGuruScraper(BaseScraper):
    source_name = "propertyguru"

    async def search(
        self,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        bedrooms: Optional[int] = None,
        district: Optional[str] = None,
        property_type: Optional[str] = None,
        page: int = 1,
    ) -> list[Listing]:
        params = []
        if min_price:
            params.append(f"minprice={min_price}")
        if max_price:
            params.append(f"maxprice={max_price}")
        if bedrooms is not None:
            params.append(f"beds={bedrooms}")
        if page > 1:
            params.append(f"page={page}")
        url = SEARCH_URL + ("?" + "&".join(params) if params else "")

        browser = await get_browser()
        ctx = await new_context(browser)
        try:
            pg = await ctx.new_page()
            await pg.goto(url, wait_until="domcontentloaded", timeout=30000)
            # Wait for listing cards to appear
            await pg.wait_for_selector(
                "[da-listing-id]",
                timeout=15000,
            )
            # Small human-like pause
            await asyncio.sleep(1.5)
            listings = await pg.evaluate(self._extract_js())
            return [self._to_listing(d) for d in listings if d.get("price")]
        except Exception as e:
            logger.error(f"[PropertyGuru] scrape failed: {e}", exc_info=True)
            return []
        finally:
            await ctx.close()

    def _extract_js(self) -> str:
        """JavaScript run in the page to extract listing data using da-id attributes."""
        return """
        () => {
            const cards = document.querySelectorAll('[da-listing-id]');
            return Array.from(cards).map(card => {
                const listingId = card.getAttribute('da-listing-id') || '';
                const priceEl = card.querySelector('[da-id="listing-card-v2-price"]');
                const titleEl = card.querySelector('[da-id="listing-card-v2-title"]');
                const addrEl  = card.querySelector('.listing-address');
                const bedEl   = card.querySelector('[da-id="listing-card-v2-bedrooms"]');
                const bathEl  = card.querySelector('[da-id="listing-card-v2-bathrooms"]');
                const areaEl  = card.querySelector('[da-id="listing-card-v2-floorarea"]');
                const linkEl  = card.querySelector('a[href*="/listing/"]');
                const imgEl   = card.querySelector('img[src*="pgimgs"]');

                const priceText = priceEl ? priceEl.innerText.replace(/[^0-9]/g, '') : '0';
                const url = linkEl ? linkEl.href
                    : (listingId ? 'https://www.propertyguru.com.sg/listing/' + listingId : '');

                return {
                    listing_id: listingId,
                    title:    titleEl ? titleEl.innerText.trim() : '',
                    url,
                    price:    parseInt(priceText) || 0,
                    address:  addrEl  ? addrEl.innerText.trim()  : '',
                    bedrooms: bedEl   ? parseInt(bedEl.innerText)  || null : null,
                    bathrooms:bathEl  ? parseInt(bathEl.innerText) || null : null,
                    area:     areaEl  ? parseInt(areaEl.innerText.replace(/[^0-9]/g, '')) || null : null,
                    image:    imgEl   ? imgEl.src : '',
                };
            });
        }
        """

    def _to_listing(self, d: dict) -> Listing:
        uid = hashlib.md5(f"pg:{d.get('listing_id') or d.get('url')}".encode()).hexdigest()[:12]
        return Listing(
            id=uid,
            source=self.source_name,
            title=d.get("title") or "Untitled",
            url=d.get("url") or "",
            price=d.get("price", 0),
            address=d.get("address") or "",
            bedrooms=d.get("bedrooms"),
            bathrooms=d.get("bathrooms"),
            area_sqft=d.get("area"),
            images=[d["image"]] if d.get("image") else [],
        )

    async def get_listing_detail(self, url: str) -> Optional[Listing]:
        return None
