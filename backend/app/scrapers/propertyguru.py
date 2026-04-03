import hashlib
import httpx
from bs4 import BeautifulSoup
from typing import Optional
from .base import BaseScraper
from ..models.listing import Listing

BASE_URL = "https://www.propertyguru.com.sg"
SEARCH_URL = f"{BASE_URL}/property-for-rent"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-SG,en;q=0.9",
}


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
        params: dict = {"market": "residential", "listing_type": "rent", "page": page}
        if min_price:
            params["minprice"] = min_price
        if max_price:
            params["maxprice"] = max_price
        if bedrooms:
            params["beds"] = bedrooms

        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=20) as client:
            resp = await client.get(SEARCH_URL, params=params)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        return self._parse_listings(soup)

    def _parse_listings(self, soup: BeautifulSoup) -> list[Listing]:
        listings = []
        cards = soup.select("div[data-listing-id]")
        for card in cards:
            try:
                listing = self._parse_card(card)
                if listing:
                    listings.append(listing)
            except Exception:
                continue
        return listings

    def _parse_card(self, card) -> Optional[Listing]:
        listing_id = card.get("data-listing-id", "")
        title_el = card.select_one("h3.listing-card__title a, a[data-listing-id]")
        title = title_el.get_text(strip=True) if title_el else "Unknown"
        url = title_el.get("href", "") if title_el else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        price_el = card.select_one("span.price")
        price_text = price_el.get_text(strip=True).replace(",", "").replace("$", "") if price_el else "0"
        price = int("".join(filter(str.isdigit, price_text)) or "0")

        addr_el = card.select_one("span.listing-location")
        address = addr_el.get_text(strip=True) if addr_el else ""

        bed_el = card.select_one("span.bed")
        bedrooms = int(bed_el.get_text(strip=True) or 0) if bed_el else None

        bath_el = card.select_one("span.bath")
        bathrooms = int(bath_el.get_text(strip=True) or 0) if bath_el else None

        area_el = card.select_one("span.floor-area")
        area_text = area_el.get_text(strip=True) if area_el else ""
        area = int("".join(filter(str.isdigit, area_text)) or 0) or None

        img_el = card.select_one("img[src]")
        images = [img_el["src"]] if img_el else []

        uid = hashlib.md5(f"propertyguru:{listing_id or url}".encode()).hexdigest()[:12]

        return Listing(
            id=uid,
            source=self.source_name,
            title=title,
            url=url,
            price=price,
            address=address,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            area_sqft=area,
            images=images,
        )

    async def get_listing_detail(self, url: str) -> Optional[Listing]:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=20) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        # Detailed parsing can be extended here
        return self._parse_card(soup.select_one("div[data-listing-id]"))
