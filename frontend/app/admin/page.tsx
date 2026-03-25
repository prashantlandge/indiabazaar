"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Upload, BarChart3, Database, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";

export default function AdminPage() {
  const [stats, setStats] = useState<{
    total_suppliers: number;
    total_products: number;
    total_searches: number;
    cities_covered: number;
    top_searches: { query: string; count: number }[];
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-4">
          <Link href="/"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <h1 className="font-display text-xl font-bold">Admin Panel</h1>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
        {/* Stats */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {loading ? (
            [1,2,3,4].map(i => <Skeleton key={i} className="h-24 rounded-lg" />)
          ) : (
            <>
              <Card>
                <CardContent className="flex items-center gap-4 p-5">
                  <Database className="h-8 w-8 text-brand-500" />
                  <div>
                    <p className="text-2xl font-bold">{stats?.total_suppliers?.toLocaleString() || 0}</p>
                    <p className="text-sm text-gray-500">Suppliers</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="flex items-center gap-4 p-5">
                  <Database className="h-8 w-8 text-emerald-500" />
                  <div>
                    <p className="text-2xl font-bold">{stats?.total_products?.toLocaleString() || 0}</p>
                    <p className="text-sm text-gray-500">Products</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="flex items-center gap-4 p-5">
                  <Search className="h-8 w-8 text-amber-500" />
                  <div>
                    <p className="text-2xl font-bold">{stats?.total_searches?.toLocaleString() || 0}</p>
                    <p className="text-sm text-gray-500">Searches</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="flex items-center gap-4 p-5">
                  <BarChart3 className="h-8 w-8 text-purple-500" />
                  <div>
                    <p className="text-2xl font-bold">{stats?.cities_covered || 0}</p>
                    <p className="text-sm text-gray-500">Cities</p>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Navigation cards */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/admin/ingestion">
            <Card className="cursor-pointer transition-shadow hover:shadow-elevated">
              <CardContent className="flex items-center gap-4 p-6">
                <Upload className="h-10 w-10 text-brand-500" />
                <div>
                  <h3 className="font-semibold text-lg">Data Ingestion</h3>
                  <p className="text-sm text-gray-500">Upload supplier data (JSON/CSV) from scraper</p>
                </div>
              </CardContent>
            </Card>
          </Link>
          <Link href="/admin/analytics">
            <Card className="cursor-pointer transition-shadow hover:shadow-elevated">
              <CardContent className="flex items-center gap-4 p-6">
                <BarChart3 className="h-10 w-10 text-emerald-500" />
                <div>
                  <h3 className="font-semibold text-lg">Search Analytics</h3>
                  <p className="text-sm text-gray-500">View search trends, top queries, and insights</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Top searches */}
        {stats?.top_searches && stats.top_searches.length > 0 && (
          <Card>
            <CardHeader><CardTitle>Top Search Queries</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                {stats.top_searches.map((s, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700 dark:text-gray-300">{s.query}</span>
                    <span className="text-gray-400">{s.count} searches</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
