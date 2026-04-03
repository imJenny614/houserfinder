from pydantic import BaseModel, HttpUrl
from typing import Optional


class Listing(BaseModel):
    id: str
    source: str  # "propertyguru" | "99co" | "edgeprop"
    title: str
    url: str
    price: int  # SGD per month
    address: str
    district: Optional[str] = None
    postal_code: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area_sqft: Optional[int] = None
    property_type: Optional[str] = None  # HDB, Condo, Landed, etc.
    furnishing: Optional[str] = None  # Fully, Partially, Unfurnished
    available_from: Optional[str] = None
    amenities: list[str] = []
    images: list[str] = []
    description: Optional[str] = None


class SearchRequest(BaseModel):
    query: str  # Natural language description from user
    max_price: Optional[int] = None
    min_price: Optional[int] = None
    bedrooms: Optional[int] = None
    district: Optional[str] = None
    property_type: Optional[str] = None


class SearchResponse(BaseModel):
    listings: list[Listing]
    total: int
    ai_summary: Optional[str] = None
