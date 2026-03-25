"use client";

import { CheckSquare, Square, SlidersHorizontal } from "lucide-react";
import type { AvailableFilters, SearchFilters as Filters } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Props {
  filters: Filters;
  available: AvailableFilters;
  onChange: (filters: Filters) => void;
}

export function SearchFilters({ filters, available, onChange }: Props) {
  const toggleArrayFilter = (key: "city" | "certifications" | "nature_of_business", value: string) => {
    const current = filters[key] || [];
    const next = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    onChange({ ...filters, [key]: next.length ? next : undefined });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-sm font-semibold text-gray-900 dark:text-gray-100">
        <SlidersHorizontal className="h-4 w-4" />
        Filters
      </div>

      {/* Verified only */}
      <div>
        <button
          onClick={() => onChange({ ...filters, verified_only: !filters.verified_only })}
          className="flex items-center gap-2 text-sm text-gray-700 hover:text-gray-900 dark:text-gray-300"
        >
          {filters.verified_only ? (
            <CheckSquare className="h-4 w-4 text-brand-500" />
          ) : (
            <Square className="h-4 w-4 text-gray-400" />
          )}
          Verified suppliers only
        </button>
      </div>

      {/* Trust score */}
      <div>
        <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-gray-500">
          Min Trust Score
        </label>
        <input
          type="range"
          min={0}
          max={100}
          step={10}
          value={filters.min_trust_score || 0}
          onChange={(e) => onChange({ ...filters, min_trust_score: Number(e.target.value) || undefined })}
          className="w-full accent-brand-500"
        />
        <div className="flex justify-between text-xs text-gray-400">
          <span>0</span>
          <span className="font-medium text-brand-600">{filters.min_trust_score || 0}</span>
          <span>100</span>
        </div>
      </div>

      {/* Cities */}
      {available.cities.length > 0 && (
        <FilterSection
          title="Location"
          options={available.cities}
          selected={filters.city || []}
          onToggle={(v) => toggleArrayFilter("city", v)}
        />
      )}

      {/* Certifications */}
      {available.certifications.length > 0 && (
        <FilterSection
          title="Certifications"
          options={available.certifications}
          selected={filters.certifications || []}
          onToggle={(v) => toggleArrayFilter("certifications", v)}
        />
      )}

      {/* Business type */}
      {available.nature_of_business.length > 0 && (
        <FilterSection
          title="Business Type"
          options={available.nature_of_business}
          selected={filters.nature_of_business || []}
          onToggle={(v) => toggleArrayFilter("nature_of_business", v)}
        />
      )}
    </div>
  );
}

function FilterSection({
  title,
  options,
  selected,
  onToggle,
}: {
  title: string;
  options: { value: string; count: number }[];
  selected: string[];
  onToggle: (value: string) => void;
}) {
  return (
    <div>
      <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-gray-500">
        {title}
      </label>
      <div className="space-y-1 max-h-48 overflow-y-auto">
        {options.slice(0, 10).map((opt) => (
          <button
            key={opt.value}
            onClick={() => onToggle(opt.value)}
            className={cn(
              "flex w-full items-center justify-between rounded-md px-2 py-1.5 text-sm transition-colors",
              selected.includes(opt.value)
                ? "bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300"
                : "text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800"
            )}
          >
            <span className="truncate">{opt.value}</span>
            <span className="ml-2 flex-shrink-0 text-xs text-gray-400">{opt.count}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
