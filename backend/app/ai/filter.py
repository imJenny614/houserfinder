import json
from anthropic import AsyncAnthropic
from ..models.listing import Listing, SearchRequest

SYSTEM_PROMPT = """You are a Singapore rental property expert. Your job is to:
1. Parse the user's natural language rental requirements
2. Score and rank listings based on how well they match the requirements
3. Provide a concise summary explaining your recommendations

When scoring listings, consider: price, location, size, property type, amenities, and any specific preferences mentioned.
Always respond in JSON format."""


async def extract_filters(query: str, client: AsyncAnthropic) -> dict:
    """Extract structured search filters from a natural language query."""
    message = await client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Extract rental search filters from this query: '{query}'\n\n"
                    "Return JSON with these optional fields:\n"
                    "- min_price (int, SGD/month)\n"
                    "- max_price (int, SGD/month)\n"
                    "- bedrooms (int)\n"
                    "- district (string, e.g. 'D10', 'Orchard')\n"
                    "- property_type (string: HDB/Condo/Landed)\n"
                    "- keywords (list of strings for amenity/feature requirements)"
                ),
            }
        ],
    )
    try:
        raw = message.content[0].text
        # Extract JSON from the response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end]) if start != -1 else {}
    except Exception:
        return {}


async def rank_listings(
    listings: list[Listing],
    request: SearchRequest,
    client: AsyncAnthropic,
) -> tuple[list[Listing], str]:
    """Use Claude to rank listings and generate a summary."""
    if not listings:
        return [], "No listings found matching your criteria."

    listings_data = [
        {
            "id": l.id,
            "title": l.title,
            "price": l.price,
            "address": l.address,
            "bedrooms": l.bedrooms,
            "bathrooms": l.bathrooms,
            "area_sqft": l.area_sqft,
            "property_type": l.property_type,
            "furnishing": l.furnishing,
            "amenities": l.amenities,
            "source": l.source,
        }
        for l in listings[:30]  # Limit to avoid token overflow
    ]

    message = await client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"User's requirement: '{request.query}'\n\n"
                    f"Available listings:\n{json.dumps(listings_data, indent=2)}\n\n"
                    "Rank these listings by relevance and return JSON:\n"
                    "{\n"
                    '  "ranked_ids": ["id1", "id2", ...],\n'
                    '  "summary": "2-3 sentence explanation of top picks"\n'
                    "}"
                ),
            }
        ],
    )

    try:
        raw = message.content[0].text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])
        ranked_ids = result.get("ranked_ids", [])
        summary = result.get("summary", "")

        id_to_listing = {l.id: l for l in listings}
        ranked = [id_to_listing[rid] for rid in ranked_ids if rid in id_to_listing]
        # Append any listings not returned by AI at the end
        ranked_set = set(ranked_ids)
        ranked += [l for l in listings if l.id not in ranked_set]

        return ranked, summary
    except Exception:
        return listings, "Here are the listings matching your search."
