"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { Listing, SearchResponse, aiSearch, getListings } from "@/lib/api";
import SearchBar from "@/components/SearchBar";
import ListingCard from "@/components/ListingCard";
import PriceChart from "@/components/PriceChart";

// Leaflet must be loaded client-side only (no SSR)
const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

type ViewMode = "grid" | "list";

export default function HomePage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [aiSummary, setAiSummary] = useState<string>("");
  const [selectedId, setSelectedId] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [viewMode, setViewMode] = useState<ViewMode>("grid");

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(undefined);
    setAiSummary("");
    try {
      const result: SearchResponse = await aiSearch({ query });
      setListings(result.listings);
      setAiSummary(result.ai_summary ?? "");
    } catch {
      setError("Search failed. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleBrowse = async () => {
    setLoading(true);
    setError(undefined);
    try {
      const result = await getListings({});
      setListings(result);
    } catch {
      setError("Failed to load listings.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold text-gray-900">HouserFinder</h1>
              <p className="text-xs text-gray-500">Singapore Rental Search</p>
            </div>
            <button
              onClick={handleBrowse}
              className="text-sm text-brand-600 hover:underline"
            >
              Browse all
            </button>
          </div>
          <SearchBar onSearch={handleSearch} loading={loading} />
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* AI Summary */}
        {aiSummary && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
            <span className="font-semibold">AI Insight: </span>
            {aiSummary}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {listings.length > 0 && (
          <>
            {/* Charts & Map */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <PriceChart listings={listings} selectedId={selectedId} />
              <MapView
                listings={listings}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                {listings.length} listings found
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode("grid")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    viewMode === "grid"
                      ? "bg-brand-600 text-white border-brand-600"
                      : "bg-white text-gray-600 border-gray-200"
                  }`}
                >
                  Grid
                </button>
                <button
                  onClick={() => setViewMode("list")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    viewMode === "list"
                      ? "bg-brand-600 text-white border-brand-600"
                      : "bg-white text-gray-600 border-gray-200"
                  }`}
                >
                  List
                </button>
              </div>
            </div>

            {/* Listings */}
            <div
              className={
                viewMode === "grid"
                  ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
                  : "flex flex-col gap-3"
              }
            >
              {listings.map((listing) => (
                <ListingCard
                  key={listing.id}
                  listing={listing}
                  selected={listing.id === selectedId}
                  onClick={() =>
                    setSelectedId(listing.id === selectedId ? undefined : listing.id)
                  }
                />
              ))}
            </div>
          </>
        )}

        {!loading && listings.length === 0 && !error && (
          <div className="text-center py-24 text-gray-400">
            <p className="text-lg font-medium">Find your next home in Singapore</p>
            <p className="text-sm mt-1">
              Describe what you&apos;re looking for above, or click &quot;Browse all&quot; to start exploring.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
