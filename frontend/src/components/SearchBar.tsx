"use client";

import { useState, FormEvent } from "react";
import { Search, Loader2 } from "lucide-react";

interface Props {
  onSearch: (query: string) => void;
  loading?: boolean;
}

export default function SearchBar({ onSearch, loading }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="relative flex-1">
        <Search
          size={18}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
        />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. 2-bedroom condo near MRT, budget $3000, fully furnished…"
          className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
        />
      </div>
      <button
        type="submit"
        disabled={loading || !query.trim()}
        className="px-5 py-3 rounded-xl bg-brand-600 text-white font-semibold text-sm disabled:opacity-60 hover:bg-brand-700 transition-colors flex items-center gap-2"
      >
        {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
        Search
      </button>
    </form>
  );
}
