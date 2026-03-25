"use client";

import { Sparkles } from "lucide-react";
import type { QueryUnderstanding } from "@/lib/api";

interface Props {
  understanding: QueryUnderstanding;
  onEdit?: () => void;
}

export function QueryUnderstandingBanner({ understanding, onEdit }: Props) {
  if (!understanding.intent_parsed) return null;

  const parts: string[] = [];
  if (understanding.product) parts.push(understanding.product);
  if (understanding.filters_applied.length > 0) {
    parts.push(...understanding.filters_applied);
  }

  if (parts.length === 0) return null;

  return (
    <div className="rounded-lg border border-brand-200 bg-brand-50 p-4 dark:border-brand-800 dark:bg-brand-950">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          <Sparkles className="mt-0.5 h-4 w-4 flex-shrink-0 text-brand-500" />
          <div>
            <p className="text-sm font-medium text-brand-800 dark:text-brand-200">
              We searched for:{" "}
              {parts.map((part, i) => (
                <span key={i}>
                  {i > 0 && <span className="mx-1 text-brand-400">·</span>}
                  <span className="font-semibold">{part}</span>
                </span>
              ))}
            </p>
            {understanding.expanded_to && understanding.expanded_to !== understanding.product && (
              <p className="mt-1 text-xs text-brand-600 dark:text-brand-400">
                Also searching for: {understanding.expanded_to}
              </p>
            )}
          </div>
        </div>
        {onEdit && (
          <button
            onClick={onEdit}
            className="flex-shrink-0 rounded-md border border-brand-300 px-2.5 py-1 text-xs font-medium text-brand-700 hover:bg-brand-100 dark:border-brand-700 dark:text-brand-300 dark:hover:bg-brand-900"
          >
            Edit Intent
          </button>
        )}
      </div>
    </div>
  );
}
