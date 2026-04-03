import hashlib
import httpx
from bs4 import BeautifulSoup
from typing import Optional
from .base import BaseScraper
from ..models.listing import Listing

BASE_URL = "https://www.99.co"
SEARCH_URL = f"{BASE_URL}/singapore/rent"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-SG,en;q=0.9",
}


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
        params: dict = {"page_num": page, "listing_type": "rent"}
        if min_price:
            params["price_min"] = min_price
        if max_price:
            params["price_max"] = max_price
        if bedrooms is not None:
            params["room_count"] = bedrooms

        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=20) as client:
            resp = await client.get(SEARCH_URL, params=params)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        return self._parse_listings(soup)

    def _parse_listings(self, soup: BeautifulSoup) -> list[Listing]:
        listings = []
        cards = soup.select("div.listing-card, article.listing-item")
        for card in cards:
            try:
                listing = self._parse_card(card)
                if listing:
                    listings.append(listing)
            except Exception:
                continue
        return listings

    def _parse_card(self, card) -> Optional[Listing]:
        title_el = card.select_one("h3 a, .listing-title a")
        title = title_el.get_text(strip=True) if title_el else "Unknown"
        url = title_el.get("href", "") if title_el else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        price_el = card.select_one(".listing-price, [class*='price']")
        price_text = price_el.get_text(strip=True) if price_el else "0"
        price = int("".join(filter(str.isdigit, price_text.replace(",", ""))) or "0")

        addr_el = card.select_one(".listing-address, [class*='address']")
        address = addr_el.get_text(strip=True) if addr_el else ""

        bed_el = card.select_one("[class*='bed']")
        bedrooms = int("".join(filter(str.isdigit, bed_el.get_text())) or 0) if bed_el else None

        bath_el = card.select_one("[class*='bath']")
        bathrooms = int("".join(filter(str.isdigit, bath_el.get_text())) or 0) if bath_el else None

        img_el = card.select_one("img[src]")
        images = [img_el["src"]] if img_el else []

        uid = hashlib.md5(f"99co:{url}".encode()).hexdigest()[:12]

        return Listing(
            id=uid,
            source=self.source_name,
            title=title,
            url=url,
            price=price,
            address=address,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            images=images,
        )

    async def get_listing_detail(self, url: str) -> Optional[Listing]:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=20) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select("div.listing-card, article.listing-item")
        return self._parse_card(cards[0]) if cards else None
