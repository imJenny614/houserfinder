"use client";

import { Listing } from "@/lib/api";
import { BedDouble, Bath, Maximize2, MapPin, ExternalLink } from "lucide-react";
import clsx from "clsx";

const SOURCE_LABELS: Record<string, string> = {
  propertyguru: "PropertyGuru",
  "99co": "99.co",
  edgeprop: "EdgeProp",
};

const SOURCE_COLORS: Record<string, string> = {
  propertyguru: "bg-green-100 text-green-700",
  "99co": "bg-blue-100 text-blue-700",
  edgeprop: "bg-purple-100 text-purple-700",
};

interface Props {
  listing: Listing;
  selected?: boolean;
  onClick?: () => void;
}

export default function ListingCard({ listing, selected, onClick }: Props) {
  return (
    <div
      className={clsx(
        "rounded-xl border bg-white shadow-sm cursor-pointer transition-all hover:shadow-md",
        selected && "ring-2 ring-brand-500"
      )}
      onClick={onClick}
    >
      {/* Image */}
      <div className="relative h-44 bg-gray-100 rounded-t-xl overflow-hidden">
        {listing.images[0] ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={listing.images[0]}
            alt={listing.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
            No image
          </div>
        )}
        <span
          className={clsx(
            "absolute top-2 left-2 text-xs font-semibold px-2 py-0.5 rounded-full",
            SOURCE_COLORS[listing.source] ?? "bg-gray-100 text-gray-600"
          )}
        >
          {SOURCE_LABELS[listing.source] ?? listing.source}
        </span>
      </div>

      {/* Body */}
      <div className="p-4 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-sm text-gray-900 line-clamp-2 leading-tight">
            {listing.title}
          </h3>
          <a
            href={listing.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="shrink-0 text-gray-400 hover:text-brand-500"
          >
            <ExternalLink size={14} />
          </a>
        </div>

        <p className="text-2xl font-bold text-brand-600">
          ${listing.price.toLocaleString()}
          <span className="text-sm font-normal text-gray-500">/mo</span>
        </p>

        <div className="flex items-center gap-1 text-gray-500 text-xs">
          <MapPin size={12} />
          <span className="truncate">{listing.address}</span>
        </div>

        <div className="flex items-center gap-3 text-gray-600 text-xs pt-1">
          {listing.bedrooms !== undefined && (
            <span className="flex items-center gap-1">
              <BedDouble size={13} />
              {listing.bedrooms} bed
            </span>
          )}
          {listing.bathrooms !== undefined && (
            <span className="flex items-center gap-1">
              <Bath size={13} />
              {listing.bathrooms} bath
            </span>
          )}
          {listing.area_sqft && (
            <span className="flex items-center gap-1">
              <Maximize2 size={13} />
              {listing.area_sqft.toLocaleString()} sqft
            </span>
          )}
        </div>

        {listing.property_type && (
          <span className="inline-block text-xs bg-gray-100 text-gray-600 rounded px-2 py-0.5">
            {listing.property_type}
          </span>
        )}
      </div>
    </div>
  );
}
