"use client";

import Link from "next/link";
import { ArrowLeft, Search, Bookmark, FileText, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-4">
          <Link href="/"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <h1 className="font-display text-xl font-bold">Dashboard</h1>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Link href="/search">
            <Card className="transition-shadow hover:shadow-elevated cursor-pointer">
              <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-950">
                  <Search className="h-6 w-6 text-brand-500" />
                </div>
                <div>
                  <h3 className="font-semibold">Search Suppliers</h3>
                  <p className="text-sm text-gray-500">Find suppliers using AI-powered search</p>
                </div>
              </CardContent>
            </Card>
          </Link>

          <Link href="/dashboard/saved">
            <Card className="transition-shadow hover:shadow-elevated cursor-pointer">
              <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-amber-50 dark:bg-amber-950">
                  <Bookmark className="h-6 w-6 text-amber-500" />
                </div>
                <div>
                  <h3 className="font-semibold">Saved Suppliers</h3>
                  <p className="text-sm text-gray-500">View your bookmarked suppliers</p>
                </div>
              </CardContent>
            </Card>
          </Link>

          <Link href="/dashboard/rfqs">
            <Card className="transition-shadow hover:shadow-elevated cursor-pointer">
              <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-50 dark:bg-emerald-950">
                  <FileText className="h-6 w-6 text-emerald-500" />
                </div>
                <div>
                  <h3 className="font-semibold">My RFQs</h3>
                  <p className="text-sm text-gray-500">Track your quote requests</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  );
}
