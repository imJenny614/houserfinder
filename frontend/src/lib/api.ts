const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Listing {
  id: string;
  source: string;
  title: string;
  url: string;
  price: number;
  address: string;
  district?: string;
  postal_code?: string;
  lat?: number;
  lng?: number;
  bedrooms?: number;
  bathrooms?: number;
  area_sqft?: number;
  property_type?: string;
  furnishing?: string;
  available_from?: string;
  amenities: string[];
  images: string[];
  description?: string;
}

export interface SearchResponse {
  listings: Listing[];
  total: number;
  ai_summary?: string;
}

export async function getListings(params: {
  min_price?: number;
  max_price?: number;
  bedrooms?: number;
  district?: string;
  property_type?: string;
  page?: number;
}): Promise<Listing[]> {
  const qs = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params)
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    )
  ).toString();
  const res = await fetch(`${API_URL}/api/v1/listings?${qs}`);
  if (!res.ok) throw new Error("Failed to fetch listings");
  return res.json();
}

export async function aiSearch(payload: {
  query: string;
  max_price?: number;
  min_price?: number;
  bedrooms?: number;
  district?: string;
  property_type?: string;
}): Promise<SearchResponse> {
  const res = await fetch(`${API_URL}/api/v1/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("AI search failed");
  return res.json();
}
