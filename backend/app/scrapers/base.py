from abc import ABC, abstractmethod
from typing import Optional
from ..models.listing import Listing


class BaseScraper(ABC):
    """Base class for all rental site scrapers."""

    source_name: str = ""

    @abstractmethod
    async def search(
        self,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        bedrooms: Optional[int] = None,
        district: Optional[str] = None,
        property_type: Optional[str] = None,
        page: int = 1,
    ) -> list[Listing]:
        """Fetch listings matching the given filters."""
        ...

    @abstractmethod
    async def get_listing_detail(self, url: str) -> Optional[Listing]:
        """Fetch full details for a single listing."""
        ...
