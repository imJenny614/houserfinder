"use client";

import { useEffect } from "react";
import { Listing } from "@/lib/api";

interface Props {
  listings: Listing[];
  selectedId?: string;
  onSelect?: (id: string) => void;
}

// Leaflet must be loaded client-side only
export default function MapView({ listings, selectedId, onSelect }: Props) {
  useEffect(() => {
    let map: import("leaflet").Map;

    (async () => {
      const L = (await import("leaflet")).default;
      await import("leaflet/dist/leaflet.css" as never);

      // Fix default icon paths broken by webpack
      // @ts-expect-error _getIconUrl missing in types
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      map = L.map("map-container").setView([1.3521, 103.8198], 12);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(map);

      listings
        .filter((l) => l.lat && l.lng)
        .forEach((l) => {
          const marker = L.marker([l.lat!, l.lng!])
            .addTo(map)
            .bindPopup(
              `<b>${l.title}</b><br/>$${l.price.toLocaleString()}/mo<br/>${l.address}`
            );
          marker.on("click", () => onSelect?.(l.id));
          if (l.id === selectedId) marker.openPopup();
        });
    })();

    return () => {
      map?.remove();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listings, selectedId]);

  return (
    <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
      <h2 className="font-semibold text-gray-800 p-4 pb-0">Map</h2>
      <div id="map-container" className="h-72 w-full" />
    </div>
  );
}
