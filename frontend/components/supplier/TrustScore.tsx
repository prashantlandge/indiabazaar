"use client";

import { Shield, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

export function TrustScore({ score, size = "md", showLabel = true }: Props) {
  const getColor = () => {
    if (score >= 70) return "text-emerald-600 dark:text-emerald-400";
    if (score >= 40) return "text-amber-600 dark:text-amber-400";
    return "text-red-500 dark:text-red-400";
  };

  const getBgColor = () => {
    if (score >= 70) return "bg-emerald-50 dark:bg-emerald-950";
    if (score >= 40) return "bg-amber-50 dark:bg-amber-950";
    return "bg-red-50 dark:bg-red-950";
  };

  const Icon = score >= 70 ? ShieldCheck : Shield;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 rounded-full font-semibold",
        getBgColor(),
        getColor(),
        size === "sm" && "px-2 py-0.5 text-xs",
        size === "md" && "px-2.5 py-1 text-sm",
        size === "lg" && "px-3 py-1.5 text-base",
      )}
    >
      <Icon className={cn(size === "sm" ? "h-3 w-3" : size === "md" ? "h-4 w-4" : "h-5 w-5")} />
      <span>{score}</span>
      {showLabel && <span className="font-normal opacity-70">/100</span>}
    </div>
  );
}

export function TrustBreakdown({ breakdown }: { breakdown: Record<string, unknown> }) {
  const items = [
    { label: "GST Verified", value: breakdown.gst_verified, max: 20 },
    { label: "Platform Verified", value: breakdown.indiamart_verified, max: 15 },
    { label: "Rating", value: breakdown.rating ? `${breakdown.rating}/5` : "N/A", max: 20 },
    { label: "Reviews", value: breakdown.num_reviews || 0, max: 10 },
    { label: "Certifications", value: (breakdown.certifications as string[])?.length || 0, max: 10 },
    { label: "Profile Complete", value: `${breakdown.profile_completeness}%`, max: 10 },
    { label: "Years Active", value: breakdown.years_in_business || "N/A", max: 10 },
  ];

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Trust Score Breakdown</h4>
      <div className="space-y-2">
        {items.map((item) => {
          const isBoolean = typeof item.value === "boolean";
          const filled = isBoolean ? (item.value ? 100 : 0) : 60;

          return (
            <div key={item.label} className="flex items-center gap-3 text-sm">
              <span className="w-32 flex-shrink-0 text-gray-600 dark:text-gray-400">{item.label}</span>
              <div className="flex-1">
                <div className="h-2 rounded-full bg-gray-100 dark:bg-gray-800">
                  <div
                    className={cn(
                      "h-2 rounded-full transition-all",
                      filled >= 70 ? "bg-emerald-500" : filled >= 40 ? "bg-amber-500" : "bg-red-400"
                    )}
                    style={{ width: `${filled}%` }}
                  />
                </div>
              </div>
              <span className="w-16 flex-shrink-0 text-right text-xs text-gray-500">
                {isBoolean ? (item.value ? "Yes" : "No") : String(item.value)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
