import hashlib
import asyncio
from typing import Optional
from .base import BaseScraper
from .browser import get_browser, new_context
from ..models.listing import Listing

SEARCH_URL = "https://www.99.co/singapore/rent"


class NinetyNineScraper(BaseScraper):
    source_name = "99co"

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
            params.append(f"price_min={min_price}")
        if max_price:
            params.append(f"price_max={max_price}")
        if bedrooms is not None:
            params.append(f"room_count_min={bedrooms}&room_count_max={bedrooms}")
        if page > 1:
            params.append(f"page_num={page}")
        url = SEARCH_URL + ("?" + "&".join(params) if params else "")

        browser = await get_browser()
        ctx = await new_context(browser)
        try:
            pg = await ctx.new_page()
            await pg.goto(url, wait_until="domcontentloaded", timeout=30000)
            await pg.wait_for_selector(
                "[class*='listing'], [class*='property-card'], article",
                timeout=10000,
            )
            await asyncio.sleep(1.5)
            listings = await pg.evaluate(self._extract_js())
            return [self._to_listing(d) for d in listings if d.get("price")]
        except Exception:
            return []
        finally:
            await ctx.close()

    def _extract_js(self) -> str:
        return """
        () => {
            // 99.co renders listing cards as <a> tags with href containing /singapore/rent/
            const cards = document.querySelectorAll('a[href*="/singapore/rent/"]');
            const seen = new Set();
            const results = [];

            for (const card of cards) {
                const href = card.href;
                if (seen.has(href) || !href.includes('/singapore/rent/')) continue;
                seen.add(href);

                const priceEl  = card.querySelector('[class*="price"], [class*="Price"]');
                const titleEl  = card.querySelector('[class*="title"], [class*="Title"], h3, h2');
                const addrEl   = card.querySelector('[class*="address"], [class*="Address"], [class*="location"]');
                const bedEl    = card.querySelector('[class*="bed"], [class*="Bed"]');
                const bathEl   = card.querySelector('[class*="bath"], [class*="Bath"]');
                const areaEl   = card.querySelector('[class*="area"], [class*="size"], [class*="sqft"]');
                const imgEl    = card.querySelector('img[src]');

                const priceText = priceEl ? priceEl.innerText.replace(/[^0-9]/g, '') : '0';
                const price = parseInt(priceText) || 0;
                if (!price) continue;

                results.push({
                    url:      href,
                    title:    titleEl ? titleEl.innerText.trim() : '',
                    price,
                    address:  addrEl  ? addrEl.innerText.trim()  : '',
                    bedrooms: bedEl   ? parseInt(bedEl.innerText)   || null : null,
                    bathrooms:bathEl  ? parseInt(bathEl.innerText)  || null : null,
                    area:     areaEl  ? parseInt(areaEl.innerText.replace(/[^0-9]/g,'')) || null : null,
                    image:    imgEl   ? imgEl.src : '',
                });
            }
            return results;
        }
        """

    def _to_listing(self, d: dict) -> Listing:
        uid = hashlib.md5(f"99co:{d.get('url')}".encode()).hexdigest()[:12]
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
