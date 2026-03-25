"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, SearchX } from "lucide-react";
import { IntelligentSearchBar } from "@/components/search/IntelligentSearchBar";
import { SearchFilters } from "@/components/search/SearchFilters";
import { QueryUnderstandingBanner } from "@/components/search/MatchReasonCard";
import { SupplierCard } from "@/components/supplier/SupplierCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api, type SearchFilters as Filters, type SearchResponse } from "@/lib/api";
import { useSearchStore } from "@/lib/store";

export default function SearchPage() {
  const searchParams = useSearchParams();
  const q = searchParams.get("q") || "";
  const { setQuery } = useSearchStore();
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState<Filters>({});
  const [page, setPage] = useState(1);

  const doSearch = useCallback(async (query: string, f: Filters, p: number) => {
    if (!query.trim()) return;
    setIsLoading(true);
    try {
      const res = await api.search({ query, filters: f, page: p, per_page: 20 });
      setResults(res);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (q) {
      setQuery(q);
      doSearch(q, filters, page);
    }
  }, [q, filters, page, doSearch, setQuery]);

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters);
    setPage(1);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/95 backdrop-blur dark:border-gray-800 dark:bg-gray-950/95">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
          <Link href="/">
            <Button variant="ghost" size="icon" className="flex-shrink-0">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div className="flex-1">
            <IntelligentSearchBar size="compact" />
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6">
        {/* Sidebar */}
        <aside className="hidden w-72 flex-shrink-0 lg:block">
          <div className="sticky top-24 rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
            <SearchFilters
              filters={filters}
              available={results?.available_filters || { cities: [], certifications: [], nature_of_business: [], states: [] }}
              onChange={handleFilterChange}
            />
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0">
          {/* Query understanding banner */}
          {results?.query_understanding && (
            <div className="mb-4">
              <QueryUnderstandingBanner understanding={results.query_understanding} />
            </div>
          )}

          {/* Results count */}
          {results && !isLoading && (
            <p className="mb-4 text-sm text-gray-500">
              {results.total} supplier{results.total !== 1 ? "s" : ""} found
            </p>
          )}

          {/* Loading skeletons */}
          {isLoading && (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
                  <div className="flex items-start gap-3">
                    <Skeleton className="h-12 w-12 rounded-lg" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-5 w-48" />
                      <Skeleton className="h-4 w-32" />
                    </div>
                    <Skeleton className="h-8 w-16 rounded-full" />
                  </div>
                  <Skeleton className="mt-4 h-16 w-full rounded-lg" />
                  <div className="mt-3 space-y-1">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Results */}
          {!isLoading && results && results.results.length > 0 && (
            <div className="space-y-4">
              {results.results.map((result, i) => (
                <SupplierCard key={result.supplier.id} result={result} position={i + 1} />
              ))}
            </div>
          )}

          {/* Empty state */}
          {!isLoading && results && results.results.length === 0 && (
            <div className="flex flex-col items-center justify-center rounded-lg border border-gray-200 bg-white p-12 text-center dark:border-gray-800 dark:bg-gray-900">
              <SearchX className="h-12 w-12 text-gray-300 dark:text-gray-600" />
              <h3 className="mt-4 font-display text-lg font-semibold text-gray-900 dark:text-white">
                No suppliers found for &ldquo;{q}&rdquo;
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Try broadening your search or using different terms
              </p>
              {results.related_searches.length > 0 && (
                <div className="mt-4 flex flex-wrap justify-center gap-2">
                  <span className="text-xs text-gray-500">Try:</span>
                  {results.related_searches.map((s) => (
                    <Link
                      key={s}
                      href={`/search?q=${encodeURIComponent(s)}`}
                      className="rounded-full border border-gray-200 px-3 py-1 text-xs text-brand-600 hover:bg-brand-50 dark:border-gray-700"
                    >
                      {s}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Pagination */}
          {results && results.total > 20 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-500">
                Page {page} of {Math.ceil(results.total / 20)}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= Math.ceil(results.total / 20)}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          )}

          {/* Related searches */}
          {results && results.related_searches.length > 0 && results.results.length > 0 && (
            <div className="mt-8">
              <p className="mb-2 text-sm font-medium text-gray-500">Related Searches</p>
              <div className="flex flex-wrap gap-2">
                {results.related_searches.map((s) => (
                  <Link
                    key={s}
                    href={`/search?q=${encodeURIComponent(s)}`}
                    className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 hover:border-brand-300 hover:text-brand-600 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400"
                  >
                    {s}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
