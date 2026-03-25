"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";

interface Analytics {
  top_queries: { query: string; count: number }[];
  zero_result_queries: { query: string; count: number }[];
  daily_volume: { date: string; count: number }[];
}

export default function AnalyticsPage() {
  const [data, setData] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSearchAnalytics().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  const maxQueryCount = data?.top_queries?.[0]?.count || 1;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-4">
          <Link href="/admin"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <h1 className="font-display text-xl font-bold">Search Analytics</h1>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
        {loading ? (
          <div className="space-y-4">
            <Skeleton className="h-64 rounded-lg" />
            <Skeleton className="h-64 rounded-lg" />
          </div>
        ) : (
          <>
            {/* Daily volume chart (simple bar chart) */}
            {data?.daily_volume && data.daily_volume.length > 0 && (
              <Card>
                <CardHeader><CardTitle>Daily Search Volume (Last 30 Days)</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex h-40 items-end gap-1">
                    {data.daily_volume.map((d) => {
                      const maxVol = Math.max(...data.daily_volume.map((v) => v.count));
                      const height = maxVol > 0 ? (d.count / maxVol) * 100 : 0;
                      return (
                        <div
                          key={d.date}
                          className="group relative flex-1 rounded-t bg-brand-500 transition-colors hover:bg-brand-600"
                          style={{ height: `${Math.max(height, 2)}%` }}
                          title={`${d.date}: ${d.count} searches`}
                        >
                          <div className="absolute -top-8 left-1/2 hidden -translate-x-1/2 rounded bg-gray-900 px-2 py-1 text-xs text-white group-hover:block">
                            {d.count}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Top queries */}
            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader><CardTitle>Top Queries</CardTitle></CardHeader>
                <CardContent>
                  {data?.top_queries?.length ? (
                    <div className="space-y-3">
                      {data.top_queries.map((q, i) => (
                        <div key={i} className="flex items-center gap-3">
                          <span className="w-6 text-right text-xs font-medium text-gray-400">{i + 1}</span>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-700 dark:text-gray-300">{q.query}</span>
                              <span className="text-xs text-gray-400">{q.count}</span>
                            </div>
                            <div className="mt-1 h-1.5 rounded-full bg-gray-100 dark:bg-gray-800">
                              <div
                                className="h-1.5 rounded-full bg-brand-500"
                                style={{ width: `${(q.count / maxQueryCount) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No search data yet</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Zero-Result Queries</CardTitle></CardHeader>
                <CardContent>
                  {data?.zero_result_queries?.length ? (
                    <div className="space-y-2">
                      {data.zero_result_queries.map((q, i) => (
                        <div key={i} className="flex items-center justify-between rounded-lg bg-red-50 p-2 text-sm dark:bg-red-950">
                          <span className="text-red-700 dark:text-red-300">{q.query}</span>
                          <span className="text-xs text-red-400">{q.count}x</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No zero-result queries</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
