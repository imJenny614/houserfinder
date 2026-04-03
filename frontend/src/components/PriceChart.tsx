"use client";

import { Listing } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface Props {
  listings: Listing[];
  selectedId?: string;
}

export default function PriceChart({ listings, selectedId }: Props) {
  const data = listings.slice(0, 20).map((l) => ({
    id: l.id,
    name: l.title.slice(0, 20) + (l.title.length > 20 ? "…" : ""),
    price: l.price,
    source: l.source,
  }));

  return (
    <div className="bg-white rounded-xl border p-4 shadow-sm">
      <h2 className="font-semibold text-gray-800 mb-3">Price Comparison</h2>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ left: 8, right: 8, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" tick={{ fontSize: 10 }} hide />
          <YAxis
            tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
            tick={{ fontSize: 11 }}
            width={42}
          />
          <Tooltip
            formatter={(value: number) => [`$${value.toLocaleString()}/mo`, "Price"]}
            labelFormatter={(label) => label}
          />
          <Bar dataKey="price" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.id}
                fill={entry.id === selectedId ? "#0ea5e9" : "#bfdbfe"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
